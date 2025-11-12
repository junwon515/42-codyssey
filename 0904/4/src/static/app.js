document.addEventListener('DOMContentLoaded', () => {

    // === [ 1. 전역 설정 ] ===

    const API_BASE_URL = '/api/v1';
    const root = document.getElementById('app-root');
    const navLinks = document.querySelectorAll('nav a');

    // 페이지네이션 설정
    const PAGE_SIZE = 10;

    // 관리자 페이지는 URL이 아닌 내부 상태로 페이지네이션 관리
    const adminState = {
        todos: { currentPage: 1 },
        questions: { currentPage: 1 },
        answers: { currentPage: 1 }
    };

    // 전역 관리자 상태 변수
    let GLOBAL_IS_ADMIN = false;

    // === [ 2. 라우터 ] ===

    /**
     * 메인 라우터. 해시 변경을 감지하여 페이지를 렌더링합니다.
     */
    async function router() {
        root.innerHTML = '<div class="loading-spinner"></div>';

        // 페이지 렌더링 전, 관리자 상태를 먼저 확인합니다.
        await checkAdminStatus();

        // 관리자 상태에 따라 Admin 네비게이션 링크를 표시/숨김
        const adminNavLink = document.getElementById('admin-nav-link');
        if (adminNavLink) {
            // GLOBAL_IS_ADMIN이 true이면 'display'를 초기화(CSS 기본값), false이면 'none'으로 설정
            adminNavLink.style.display = GLOBAL_IS_ADMIN ? '' : 'none';
        }

        const fullHash = window.location.hash || '#/';
        const [hash, queryString] = fullHash.split('?');
        const params = new URLSearchParams(queryString || '');
        const page = parseInt(params.get('page') || '1');

        setActiveNav(hash);

        try {
            if (hash === '#/') {
                await renderTodoPage(page);
            } else if (hash === '#/todo/new') {
                await renderCreateTodoPage();
            } else if (hash === '#/questions') {
                await renderQuestionListPage(page);
            } else if (hash === '#/question/new') {
                await renderCreateQuestionPage();
            } else if (hash.startsWith('#/question/')) {
                const id = hash.split('/')[2];
                await renderQuestionDetailPage(id);
            } else if (hash === '#/admin') {
                // 관리자 페이지는 내부 상태로 페이징
                await renderAdminPage();
            } else {
                renderNotFound();
            }
        } catch (error) {
            console.error('페이지 렌더링 오류:', error);
            renderError(error.message || '페이지를 불러오는 데 실패했습니다.');
        }
    }

    /**
     * 현재 활성화된 내비게이션 링크에 'active' 클래스를 추가합니다.
     */
    function setActiveNav(hash) {
        navLinks.forEach(link => {
            // '/new' 페이지일 때도 부모 링크 활성화
            const linkHref = link.getAttribute('href');
            const isActive = (hash === linkHref) ||
                             (hash.endsWith('/new') && linkHref === hash.replace('/new', '')) ||
                             (hash.startsWith('#/question/') && linkHref === '#/questions');

            link.classList.toggle('active', isActive);
        });
    }

    window.addEventListener('hashchange', router);
    window.addEventListener('load', router);

    // === [ 3. API 및 유틸리티 헬퍼 ] ===

    /**
     * API 호출 래퍼
     */
    async function fetchAPI(endpoint, options = {}) {
        options.headers = {
            'Content-Type': 'application/json',
            ...options.headers,
        };
        const response = await fetch(`${API_BASE_URL}${endpoint}`, options);
        if (response.status === 204) return null;
        const data = await response.json();
        if (!response.ok) {
            const errorMsg = data.warning || data.error || data.detail || `HTTP Error ${response.status}`;
            throw new Error(errorMsg);
        }
        return data;
    }

    /**
     * 관리자 상태 확인
     * API를 호출하여 전역 GLOBAL_IS_ADMIN 변수를 업데이트합니다.
     */
    async function checkAdminStatus() {
        try {
            // 이 엔드포인트는 IP만 확인하므로 실패 시(404 등) 관리자가 아닌 것으로 간주
            const data = await fetchAPI('/auth/status');
            GLOBAL_IS_ADMIN = data.is_admin;
        } catch (error) {
            console.warn('Admin status check failed, assuming non-admin.', error);
            GLOBAL_IS_ADMIN = false;
        }
    }

    /**
     * 날짜 포맷팅
     */
    function formatDate(isoString) {
        if (!isoString) return 'N/A';
        try {
            return new Date(isoString).toLocaleString('ko-KR', {
                year: 'numeric', month: 'long', day: 'numeric',
                hour: '2-digit', minute: '2-digit'
            });
        } catch (e) { return isoString; }
    }

    /**
     * 뷰 토글 (인라인 수정/삭제용)
     * @param {string} containerId - The ID of the parent item (e.g., 'todo-123')
     * @param {string} modeToShow - The class of the view to show (e.g., '.inline-edit-form')
     */
    function toggleView(containerId, modeToShow) {
        const container = document.getElementById(containerId);
        if (!container) {
            console.error(`ToggleView: Container #${containerId} not found.`);
            return;
        }

        const viewMode = container.querySelector('.view-mode');
        const editForm = container.querySelector('.inline-edit-form');
        const deleteForm = container.querySelector('.inline-delete-form');

        // 1. 모든 뷰를 일단 숨깁니다.
        if (viewMode) viewMode.style.display = 'none';
        if (editForm) editForm.style.display = 'none';
        if (deleteForm) deleteForm.style.display = 'none';

        // 2. 보여줄 대상(modeToShow)을 찾습니다.
        const targetEl = container.querySelector(modeToShow);
        if (!targetEl) {
            console.error(`ToggleView: Target ${modeToShow} not found in #${containerId}.`);
            // 대상이 없으면 기본 뷰(view-mode)를 다시 보여줍니다.
            if (viewMode) viewMode.style.display = ''; // CSS 기본값(flex/block)으로 복원
            return;
        }

        // 3. 대상의 CSS display 속성을 명시적으로 설정하여 보여줍니다.
        // CSS 파일에 정의된 값을 기반으로 합니다.
        if (modeToShow === '.inline-edit-form') {
            targetEl.style.display = 'block';
        } else if (modeToShow === '.inline-delete-form') {
            targetEl.style.display = 'flex';
        } else if (modeToShow === '.view-mode') {
            // view-mode는 todo-view(flex)와 question/answer(block)가 있습니다.
            if (targetEl.classList.contains('todo-view')) {
                targetEl.style.display = 'flex';
            } else {
                targetEl.style.display = 'block';
            }
        } else {
            // 예외 상황
            targetEl.style.display = 'block';
        }
    }

    // === [ 4. 페이지 렌더링 함수 ] ===

    // --- 4-1. Todo 페이지 ---

    async function renderTodoPage(page = 1) {
        root.innerHTML = `
            <div class="container">
                <div class="list-header">
                    <h1>📋 나의 할 일</h1>
                    <a href="#/todo/new" class="btn btn-primary">새 할 일 작성</a>
                </div>
                <ul id="todo-list" class="todo-list">
                    <div class="loading-spinner"></div>
                </ul>
                <div id="pagination" class="pagination"></div>
            </div>
        `;

        await loadTodos(page);
    }

    async function loadTodos(page) {
        const listElement = document.getElementById('todo-list');
        listElement.innerHTML = '<div class="loading-spinner"></div>';

        const skip = (page - 1) * PAGE_SIZE;
        try {
            const data = await fetchAPI(`/todo/?skip=${skip}&limit=${PAGE_SIZE}`);
            const { items, total_items } = data;

            if (total_items === 0) {
                listElement.innerHTML = '<p>등록된 할 일이 없습니다.</p>';
                document.getElementById('pagination').innerHTML = '';
                return;
            }

            listElement.innerHTML = '';
            items.forEach(todo => {
                listElement.appendChild(createTodoItemElement(todo));
            });

            renderPaginationControls(document.getElementById('pagination'), '#/', page, total_items);

        } catch (error) {
            listElement.innerHTML = renderError(error.message);
        }
    }

    /**
     * Todo 항목 DOM 엘리먼트 생성 (인라인 폼 포함)
     */
    function createTodoItemElement(todo) {
        const item = document.createElement('li');
        item.className = `todo-item ${todo.is_completed ? 'completed' : ''}`;
        item.id = `todo-${todo.id}`;

        item.innerHTML = `
            <div class="view-mode todo-view">
                <input type="checkbox" class="todo-check" data-id="${todo.id}" ${todo.is_completed ? 'checked' : ''}>
                <div class="task-info">
                    <span class="task-content">${todo.task}</span>
                    <div class="due-date">${todo.due_date ? `마감: ${todo.due_date}` : ''}</div>
                    <div class="todo-meta">
                        <span>IP: ${todo.creator_ip}</span> |
                        <span>Created: ${formatDate(todo.created_at)}${todo.updated_at ? ' <small>(수정됨)</small>' : ''}</span>
                    </div>
                </div>
                <div class="actions">
                    <button class="btn btn-secondary btn-small btn-update-toggle">수정</button>
                    <button class="btn btn-danger btn-small btn-delete-toggle">삭제</button>
                    ${GLOBAL_IS_ADMIN ? `<button class="btn btn-warning btn-small btn-admin-soft-delete">관리자 삭제</button>` : ''}
                </div>
            </div>

            <form class="inline-edit-form" style="display:none;">
                <div class="form-group">
                    <label>내용</label>
                    <input type="text" name="task" class="form-control" value="${todo.task}" required>
                </div>
                <div class="form-group">
                    <label>마감일</label>
                    <input type="date" name="due_date" class="form-control" value="${todo.due_date || ''}">
                </div>
                <div class="form-group">
                    <label>비밀번호</label>
                    <input type="password" name="password" class="form-control" required>
                </div>
                <div class="form-actions">
                    <button type="submit" class="btn btn-success btn-small">저장</button>
                    <button type="button" class="btn btn-secondary btn-small btn-cancel-edit">취소</button>
                </div>
            </form>

            <form class="inline-delete-form" style="display:none;">
                <input type="password" name="password" class="form-control" placeholder="삭제 비밀번호" required>
                <button type="submit" class="btn btn-danger btn-small">확인</button>
                <button type="button" class="btn btn-secondary btn-small btn-cancel-delete">취소</button>
            </form>
        `;

        // 이벤트 리스너 바인딩
        item.querySelector('.todo-check').addEventListener('change', (e) => handleToggleTodo(todo.id, e.target));
        item.querySelector('.btn-update-toggle').addEventListener('click', () => toggleView(item.id, '.inline-edit-form'));
        item.querySelector('.btn-delete-toggle').addEventListener('click', () => toggleView(item.id, '.inline-delete-form'));

        const editForm = item.querySelector('.inline-edit-form');
        const deleteForm = item.querySelector('.inline-delete-form');
        const cancelEditBtn = item.querySelector('.inline-edit-form .btn-cancel-edit');
        const cancelDeleteBtn = item.querySelector('.inline-delete-form .btn-cancel-delete');

        editForm.onsubmit = (e) => handleUpdateTodo(e, todo.id);
        deleteForm.onsubmit = (e) => handleDeleteTodo(e, todo.id);

        cancelEditBtn.onclick = () => toggleView(item.id, '.view-mode');
        cancelDeleteBtn.onclick = () => toggleView(item.id, '.view-mode');

        if (GLOBAL_IS_ADMIN) {
            item.querySelector('.btn-admin-soft-delete').addEventListener('click', (e) => handleAdminSoftDelete(e, 'todos', todo.id));
        }

        return item;
    }

    /**
     * Todo 작성 페이지 렌더링
     */
    async function renderCreateTodoPage() {
        root.innerHTML = `
            <div class="container">
                <h1>📋 새 할 일 작성</h1>
                <form id="add-todo-form">
                    <div class="form-group">
                        <label for="task">할 일 내용</label>
                        <input type="text" id="task" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="due-date">마감일 (선택)</label>
                        <input type="date" id="due-date" class="form-control">
                    </div>
                    <div class="form-group">
                        <label for="todo-password">비밀번호</label>
                        <input type="password" id="todo-password" class="form-control" required>
                        <p class="password-prompt">수정/삭제 시 사용할 비밀번호입니다.</p>
                    </div>
                    <button type="submit" class="btn btn-primary">등록하기</button>
                    <a href="#/" class="btn btn-secondary">목록으로</a>
                </form>
            </div>
        `;
        document.getElementById('add-todo-form').addEventListener('submit', handleAddTodo);
    }

    // --- 4-2. Q&A 목록 페이지 ---

    async function renderQuestionListPage(page = 1) {
        root.innerHTML = `
            <div class="container">
                <div class="list-header">
                    <h1>❓ Q&A 게시판</h1>
                    <a href="#/question/new" class="btn btn-primary">새 질문 작성</a>
                </div>
                <ul id="question-list" class="question-list">
                    <div class="loading-spinner"></div>
                </ul>
                <div id="pagination" class="pagination"></div>
            </div>
        `;
        await loadQuestions(page);
    }

    async function loadQuestions(page) {
        const listElement = document.getElementById('question-list');
        listElement.innerHTML = '<div class="loading-spinner"></div>';

        const skip = (page - 1) * PAGE_SIZE;
        try {
            const data = await fetchAPI(`/question/?skip=${skip}&limit=${PAGE_SIZE}`);
            const { items, total_items } = data;

            if (total_items === 0) {
                listElement.innerHTML = '<p>등록된 질문이 없습니다.</p>';
                document.getElementById('pagination').innerHTML = '';
                return;
            }

            listElement.innerHTML = '';
            items.forEach(q => {
                const item = document.createElement('li');
                item.className = 'question-item';
                item.innerHTML = `
                    <a href="#/question/${q.id}">
                        <h3>${q.subject}</h3>
                        <div class="question-item-meta">
                            <span class="creator">작성자: ${q.creator_ip}</span>
                            <span>답변: ${q.answer_count}개</span>
                            <span>${formatDate(q.created_at)}</span>
                        </div>
                    </a>
                `;
                listElement.appendChild(item);
            });

            renderPaginationControls(document.getElementById('pagination'), '#/questions', page, total_items);

        } catch (error) {
            listElement.innerHTML = renderError(error.message);
        }
    }

    /**
     * Question 작성 페이지 렌더링
     */
    async function renderCreateQuestionPage() {
        root.innerHTML = `
            <div class="container">
                <h1>❓ 새 질문 작성</h1>
                <form id="add-question-form">
                    <div class="form-group">
                        <label for="subject">제목</label>
                        <input type="text" id="subject" class="form-control" required>
                    </div>
                    <div class="form-group">
                        <label for="content">내용</label>
                        <textarea id="content" class="form-control" required></textarea>
                    </div>
                    <div class="form-group">
                        <label for="question-password">비밀번호</label>
                        <input type="password" id="question-password" class="form-control" required>
                        <p class="password-prompt">수정/삭제 시 사용할 비밀번호입니다.</p>
                    </div>
                    <button type="submit" class="btn btn-primary">등록하기</button>
                    <a href="#/questions" class="btn btn-secondary">목록으로</a>
                </form>
            </div>
        `;
        document.getElementById('add-question-form').addEventListener('submit', handleAddQuestion);
    }

    // --- 4-3. Q&A 상세 페이지 ---

    async function renderQuestionDetailPage(id) {
        try {
            const q = await fetchAPI(`/question/${id}`);

            root.innerHTML = `
                <div class="container" id="question-container-${q.id}">
                    <div class="view-mode">
                        <div class="question-detail-header">
                            <h1 id="question-subject">${q.subject}</h1>
                            <div class="question-detail-meta">
                                <span>작성자: ${q.creator_ip}</span>
                                <span>작성일: ${formatDate(q.created_at)}${q.updated_at ? ` <small>(수정됨)</small>` : ''}</span>
                            </div>
                        </div>
                        <div class="question-content" id="question-content">${q.content.replace(/\n/g, '<br>')}</div>
                        <div class="question-actions answer-actions">
                            <button class="btn btn-secondary btn-update-toggle">수정</button>
                            <button class="btn btn-danger btn-delete-toggle">삭제</button>
                            ${GLOBAL_IS_ADMIN ? `<button class="btn btn-warning btn-admin-soft-delete">관리자 삭제</button>` : ''}
                        </div>
                    </div>

                    <form class="inline-edit-form" style="display:none;">
                        <div class="form-group">
                            <label>제목</label>
                            <input type="text" name="subject" class="form-control" value="${q.subject}" required>
                        </div>
                        <div class="form-group">
                            <label>내용</label>
                            <textarea name="content" class="form-control" required>${q.content}</textarea>
                        </div>
                        <div class="form-group">
                            <label>비밀번호</label>
                            <input type="password" name="password" class="form-control" required>
                        </div>
                        <div class="form-actions">
                            <button type="submit" class="btn btn-success btn-small">저장</button>
                            <button type="button" class="btn btn-secondary btn-small btn-cancel-edit">취소</button>
                        </div>
                    </form>

                    <form class="inline-delete-form" style="display:none;">
                        <input type="password" name="password" class="form-control" placeholder="삭제 비밀번호" required>
                        <button type="submit" class="btn btn-danger btn-small">삭제 확인</button>
                        <button type="button" class="btn btn-secondary btn-small btn-cancel-delete">취소</button>
                    </form>

                    <div class="answer-section">
                        <h2>답변 ${q.answer_count}개</h2>
                        <div id="answer-list"></div>
                    </div>

                    <form id="add-answer-form" class="answer-form" data-question-id="${q.id}">
                        <h2>답변 작성</h2>
                        <div class="form-group">
                            <label for="answer-content">내용</label>
                            <textarea id="answer-content" name="answer-content" class="form-control" required></textarea>
                        </div>
                        <div class="form-group">
                            <label for="answer-password">비밀번호</label>
                            <input type="password" id="answer-password" name="answer-password" class="form-control" required>
                        </div>
                        <button type="submit" class="btn btn-primary">답변 등록</button>
                    </form>
                </div>
            `;

            // 질문 수정/삭제 리스너
            const containerId = `question-container-${q.id}`;
            document.querySelector('.view-mode .btn-update-toggle').addEventListener('click', () => toggleView(containerId, '.inline-edit-form'));
            document.querySelector('.view-mode .btn-delete-toggle').addEventListener('click', () => toggleView(containerId, '.inline-delete-form'));
            document.querySelector('.inline-edit-form .btn-cancel-edit').addEventListener('click', () => toggleView(containerId, '.view-mode'));
            document.querySelector('.inline-delete-form .btn-cancel-delete').addEventListener('click', () => toggleView(containerId, '.view-mode'));

            document.querySelector('.inline-edit-form').addEventListener('submit', (e) => handleUpdateQuestion(e, q.id));
            document.querySelector('.inline-delete-form').addEventListener('submit', (e) => handleDeleteQuestion(e, q.id));

            if (GLOBAL_IS_ADMIN) {
                document.querySelector('.view-mode .btn-admin-soft-delete').addEventListener('click', (e) => handleAdminSoftDelete(e, 'questions', q.id));
            }

            // 답변 폼 리스너
            document.getElementById('add-answer-form').addEventListener('submit', handleAddAnswer);

            // 답변 목록 렌더링
            const answerListElement = document.getElementById('answer-list');
            if (q.answers && q.answers.length > 0) {
                q.answers.forEach(answer => answerListElement.appendChild(createAnswerElement(answer)));
            } else {
                answerListElement.innerHTML = '<p>등록된 답변이 없습니다.</p>';
            }

        } catch (error) {
            renderError(error.message);
        }
    }

    /**
     * (재귀) 답변 및 대댓글 DOM 엘리먼트 생성
     */
    function createAnswerElement(answer) {
        const answerElement = document.createElement('div');
        answerElement.className = 'answer-item';
        answerElement.id = `answer-${answer.id}`;

        // 6. 삭제된 답글 UI
        if (answer.deleted_at) {
            answerElement.classList.add('deleted-answer');
            answerElement.innerHTML = `
                <div class="answer-meta">
                    <span>${formatDate(answer.created_at)}</span>
                </div>
                <div class="answer-content">해당 답글은 삭제되었습니다.</div>
                <div class="replies" id="replies-for-${answer.id}"></div>
                <div class="load-more-container" id="load-more-for-${answer.id}"></div>
            `;
        } else {
            // 정상 답글
            answerElement.innerHTML = `
                <div class="view-mode">
                    <div class="answer-meta">
                        <span class="creator">작성자: ${answer.creator_ip}</span>
                        <span>${formatDate(answer.created_at)}${answer.updated_at ? ` <small>(수정됨)</small>` : ''}</span>
                    </div>
                    <div class="answer-content">${answer.content.replace(/\n/g, '<br>')}</div>
                    <div class="answer-actions">
                        <button class="btn btn-link btn-reply">답글</button>
                        <button class="btn btn-link btn-update-toggle">수정</button>
                        <button class="btn btn-link btn-delete-toggle">삭제</button>
                        ${GLOBAL_IS_ADMIN ? `<button class="btn btn-link btn-warning btn-admin-soft-delete">관리자 삭제</button>` : ''}
                        <span style="margin-left: auto;">답글 ${answer.reply_count}개</span>
                    </div>
                </div>

                <form class="inline-edit-form" style="display:none;">
                    <div class="form-group">
                        <textarea name="content" class="form-control" required>${answer.content}</textarea>
                    </div>
                    <div class="form-group">
                        <input type="password" name="password" class="form-control" placeholder="비밀번호" required>
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="btn btn-success btn-small">저장</button>
                        <button type="button" class="btn btn-secondary btn-small btn-cancel-edit">취소</button>
                    </div>
                </form>

                <form class="inline-delete-form" style="display:none;">
                    <input type="password" name="password" class="form-control" placeholder="삭제 비밀번호" required>
                    <button type="submit" class="btn btn-danger btn-small">확인</button>
                    <button type="button" class="btn btn-secondary btn-small btn-cancel-delete">취소</button>
                </form>

                <div class="reply-form-container" id="reply-form-for-${answer.id}"></div>
                <div class="replies" id="replies-for-${answer.id}"></div>
                <div class="load-more-container" id="load-more-for-${answer.id}"></div>
            `;

            // 리스너 바인딩
            answerElement.querySelector('.btn-reply').addEventListener('click', () => showReplyForm(answer.id, answer.question_id));
            answerElement.querySelector('.btn-update-toggle').addEventListener('click', () => toggleView(answerElement.id, '.inline-edit-form'));
            answerElement.querySelector('.btn-delete-toggle').addEventListener('click', () => toggleView(answerElement.id, '.inline-delete-form'));

            answerElement.querySelector('.inline-edit-form .btn-cancel-edit').addEventListener('click', () => toggleView(answerElement.id, '.view-mode'));
            answerElement.querySelector('.inline-delete-form .btn-cancel-delete').addEventListener('click', () => toggleView(answerElement.id, '.view-mode'));

            answerElement.querySelector('.inline-edit-form').addEventListener('submit', (e) => handleUpdateAnswer(e, answer.id));
            answerElement.querySelector('.inline-delete-form').addEventListener('submit', (e) => handleDeleteAnswer(e, answer.id));

            if (GLOBAL_IS_ADMIN) {
                answerElement.querySelector('.btn-admin-soft-delete').addEventListener('click', (e) => handleAdminSoftDelete(e, 'answers', answer.id));
            }
        }

        // 9. 대댓글 동적 로딩 처리
        const repliesContainer = answerElement.querySelector(`#replies-for-${answer.id}`);
        const loadMoreContainer = answerElement.querySelector(`#load-more-for-${answer.id}`);

        // 1. 사전 로드된 2단계 답글 렌더링
        if (answer.replies && answer.replies.length > 0) {
            answer.replies.forEach(reply => repliesContainer.appendChild(createAnswerElement(reply)));
        }

        // 2. 2단계 답글이 없지만, 총 갯수가 0보다 크면 '더보기' 버튼
        // (즉, 3단계 이상 답글이 존재함)
        if (answer.reply_count > answer.replies.length) {
            const button = document.createElement('button');
            button.className = 'btn btn-secondary btn-small load-more-replies';
            button.textContent = `답글 더보기 (${answer.reply_count - answer.replies.length}개)`;
            button.onclick = () => handleLoadReplies(answer.id);
            loadMoreContainer.appendChild(button);
        }

        return answerElement;
    }

    // --- 4-4. 관리자 페이지 ---

    async function renderAdminPage() {
        root.innerHTML = `
            <div class="container">
                <h1>🔒 관리자 페이지</h1>
                <p>소프트 삭제된 항목들을 영구 삭제(Hard Delete)할 수 있습니다.</p>

                <h2>삭제된 Todos</h2>
                <div id="admin-todos" class="admin-table-container"></div>
                <div id="pagination-admin-todos" class="pagination"></div>

                <h2>삭제된 Questions</h2>
                <div id="admin-questions" class="admin-table-container"></div>
                <div id="pagination-admin-questions" class="pagination"></div>

                <h2>삭제된 Answers</h2>
                <div id="admin-answers" class="admin-table-container"></div>
                <div id="pagination-admin-answers" class="pagination"></div>
            </div>
        `;

        // 3개 테이블 각각 로드
        await loadAdminTable('todos', 1);
        await loadAdminTable('questions', 1);
        await loadAdminTable('answers', 1);
    }

    async function loadAdminTable(itemType, page) {
        adminState[itemType].currentPage = page;
        const container = document.getElementById(`admin-${itemType}`);
        const paginationContainer = document.getElementById(`pagination-admin-${itemType}`);

        container.innerHTML = '<div class="loading-spinner"></div>';
        paginationContainer.innerHTML = '';

        const skip = (page - 1) * PAGE_SIZE;

        try {
            // 관리자 API는 IP 기반으로 보호됨
            // /admin/deleted-items API는 3종류를 다 반환하므로, 필요한 것만 필터링
            const data = await fetchAPI(`/admin/deleted-items?skip=${skip}&limit=${PAGE_SIZE}`);
            const { items, total_items } = data[itemType]; // 'todos', 'questions', 'answers'

            if (total_items === 0) {
                container.innerHTML = '<p>삭제된 항목이 없습니다.</p>';
                return;
            }

            let tableHTML = `
                <table>
                    <thead><tr><th>ID</th><th>내용</th><th>정보</th><th>작업</th></tr></thead>
                    <tbody>
            `;
            items.forEach(item => {
                const content = item.task || item.subject || item.content;
                tableHTML += `
                    <tr>
                        <td>${item.id}</td>
                        <td class="deleted-content">${content}</td>
                        <td class="deleted-meta">
                            IP: ${item.creator_ip}<br>Created: ${formatDate(item.created_at)}
                        </td>
                        <td>
                            <button class="btn btn-danger btn-small btn-hard-delete" data-type="${itemType}" data-id="${item.id}">
                                영구 삭제
                            </button>
                        </td>
                    </tr>
                `;
            });
            tableHTML += '</tbody></table>';
            container.innerHTML = tableHTML;

            // 관리자용 페이지네이션 렌더링 (해시 변경 X, JS 함수 호출)
            renderPaginationControls(paginationContainer, itemType, page, total_items);

            // 영구 삭제 버튼 리스너
            container.querySelectorAll('.btn-hard-delete').forEach(btn => {
                btn.addEventListener('click', (e) => {
                    const { type, id } = e.target.dataset;
                    handleHardDelete(type, id);
                });
            });

        } catch (error) {
            container.innerHTML = renderError(error.message);
        }
    }

    // --- 4-5. 404 및 에러 ---

    function renderNotFound() {
        root.innerHTML = `
            <div class="container" style="text-align: center;">
                <h1>404 Not Found</h1>
                <p>요청하신 페이지를 찾을 수 없습니다.</p>
                <a href="#/" class="btn btn-primary">홈으로 돌아가기</a>
            </div>
        `;
    }

    function renderError(message) {
        const errorHTML = `<div class="error-message"><strong>오류:</strong> ${message}</div>`;
        // 로딩 중 에러가 발생하면 root에, 목록 로딩 중 에러가 발생하면 해당 목록 컨테이너에 표시
        const listContainer = root.querySelector('.loading-spinner')?.parentElement;
        if (listContainer) {
            listContainer.innerHTML = errorHTML;
        } else {
            root.innerHTML = errorHTML;
        }
        return errorHTML;
    }

    // --- 4-6. 페이지네이션 렌더링 ---

    /**
     * 페이지네이션 UI를 렌더링합니다.
     * @param {HTMLElement} container - 페이지네이션을 그릴 엘리먼트
     * @param {string} baseHash - '#/' 또는 '#/questions'
     * @param {number} currentPage - 현재 페이지
     * @param {number} totalItems - 전체 아이템 수
     */
    function renderPaginationControls(container, baseHash, currentPage, totalItems) {
        const totalPages = Math.ceil(totalItems / PAGE_SIZE);
        if (totalPages <= 1) {
            container.innerHTML = '';
            return;
        }

        let html = '';

        // 이전 버튼
        if (currentPage > 1) {
            // 관리자 페이지는 JS 함수 호출, 나머지는 해시 변경
            if (baseHash.startsWith('#')) {
                html += `<a href="${baseHash}?page=${currentPage - 1}">&laquo; 이전</a>`;
            } else {
                html += `<a href="#" onclick="window.app.loadAdminTable('${baseHash}', ${currentPage - 1}); return false;">&laquo; 이전</a>`;
            }
        } else {
            html += `<span class="disabled">&laquo; 이전</span>`;
        }

        // 페이지 번호 (간단한 버전)
        for (let i = 1; i <= totalPages; i++) {
            if (i === currentPage) {
                html += `<span class="current">${i}</span>`;
            } else {
                if (baseHash.startsWith('#')) {
                    html += `<a href="${baseHash}?page=${i}">${i}</a>`;
                } else {
                    html += `<a href="#" onclick="window.app.loadAdminTable('${baseHash}', ${i}); return false;">${i}</a>`;
                }
            }
        }

        // 다음 버튼
        if (currentPage < totalPages) {
            if (baseHash.startsWith('#')) {
                html += `<a href="${baseHash}?page=${currentPage + 1}">다음 &raquo;</a>`;
            } else {
                html += `<a href="#" onclick="window.app.loadAdminTable('${baseHash}', ${currentPage + 1}); return false;">다음 &raquo;</a>`;
            }
        } else {
            html += `<span class="disabled">다음 &raquo;</span>`;
        }

        container.innerHTML = html;
    }

    // window.app에 함수 노출 (관리자 페이지네이션 인라인 클릭용)
    window.app = { loadAdminTable };


    // === [ 5. 이벤트 핸들러 (C, U, D) ] ===

    // --- Todo 핸들러 ---
    async function handleAddTodo(e) {
        e.preventDefault();
        const form = e.target;
        const task = form.elements.task.value;
        const dueDate = form.elements['due-date'].value || null;
        const password = form.elements['todo-password'].value;

        try {
            await fetchAPI('/todo/', {
                method: 'POST',
                body: JSON.stringify({ task, due_date: dueDate, password }),
            });
            window.location.hash = '#/'; // 등록 후 목록 1페이지로 이동
        } catch (error) {
            alert(`Todo 추가 실패: ${error.message}`);
        }
    }

    async function handleDeleteTodo(e, id) {
        e.preventDefault();
        const form = e.target;
        const password = form.elements.password.value;
        if (!password) { alert('비밀번호를 입력하세요.'); return; }

        try {
            await fetchAPI(`/todo/${id}`, {
                method: 'DELETE',
                body: JSON.stringify({ password }),
            });
            await router(); // 페이지 새로고침
        } catch (error) {
            alert(`삭제 실패: ${error.message}`);
        }
    }

    async function handleUpdateTodo(e, id) {
        e.preventDefault();
        const form = e.target;
        const task = form.elements.task.value;
        const due_date = form.elements.due_date.value || null;
        const password = form.elements.password.value;

        if (!password) { alert('비밀번호를 입력하세요.'); return; }

        try {
            await fetchAPI(`/todo/${id}`, {
                method: 'PUT',
                body: JSON.stringify({ task, due_date, password }),
            });
            await router(); // 페이지 새로고침
        } catch (error) {
            alert(`수정 실패: ${error.message}`);
        }
    }

    async function handleToggleTodo(id, checkboxElement) {
        const isCompleted = checkboxElement.checked;

        const containerId = `todo-${id}`;
        toggleView(containerId, '.inline-delete-form'); // 삭제 폼 UI 재활용
        const form = document.querySelector(`#${containerId} .inline-delete-form`);
        if (!form) return;

        const submitButton = form.querySelector('button[type="submit"]');
        const cancelButton = form.querySelector('.btn-cancel-delete');
        const passwordInput = form.querySelector('input[name="password"]');

        // 1. 기존 핸들러 임시 저장
        const originalOnSubmit = form.onsubmit;
        const originalOnCancel = cancelButton.onclick;

        // 2. UI 임시 변경 (삭제 -> 상태 변경)
        passwordInput.placeholder = '상태 변경 비밀번호';
        submitButton.textContent = '상태 변경';
        submitButton.classList.remove('btn-danger');
        submitButton.classList.add('btn-primary');

        // 3. 핸들러 정리용 함수 (취소 또는 실패 시 호출)
        const cleanup = () => {
            toggleView(containerId, '.view-mode');

            // UI 원상복구
            passwordInput.placeholder = '삭제 비밀번호';
            passwordInput.value = ''; // 비밀번호 필드 비우기
            submitButton.textContent = '확인';
            submitButton.classList.remove('btn-primary');
            submitButton.classList.add('btn-danger');

            // 핸들러 원상복구
            form.onsubmit = originalOnSubmit;
            cancelButton.onclick = originalOnCancel;
        };

        // 4. 임시 '취소' 핸들러 할당
        cancelButton.onclick = () => {
            checkboxElement.checked = !isCompleted; // 체크박스 원상복구
            cleanup();
        };

        // 5. 임시 '제출(상태변경)' 핸들러 할당
        form.onsubmit = async (e) => {
            e.preventDefault(); // 원래의 삭제 핸들러(originalOnSubmit)가 실행되지 않음
            const password = passwordInput.value;
            if (!password) {
                alert('비밀번호를 입력하세요.');
                return;
            }

            const endpoint = isCompleted ? `/todo/${id}/complete` : `/todo/${id}/uncomplete`;
            try {
                await fetchAPI(endpoint, {
                    method: 'POST',
                    body: JSON.stringify({ password }),
                });
                await router(); // 성공 (페이지 리로드하면 핸들러 자동 리셋됨)
            } catch (error) {
                alert(`상태 변경 실패: ${error.message}`);
                checkboxElement.checked = !isCompleted; // 체크박스 원상복구
                cleanup(); // 실패 시 핸들러 정리
            }
        };
    }

    // --- Question 핸들러 ---
    async function handleAddQuestion(e) {
        e.preventDefault();
        const form = e.target;
        const subject = form.elements.subject.value;
        const content = form.elements.content.value;
        const password = form.elements['question-password'].value;

        try {
            await fetchAPI('/question/', {
                method: 'POST',
                body: JSON.stringify({ subject, content, password }),
            });
            window.location.hash = '#/questions'; // 목록 1페이지로 이동
        } catch (error) {
            alert(`질문 등록 실패: ${error.message}`);
        }
    }

    async function handleDeleteQuestion(e, id) {
        e.preventDefault();
        const password = e.target.elements.password.value;
        if (!password) { alert('비밀번호를 입력하세요.'); return; }

        if (!confirm('정말로 이 질문을 삭제하시겠습니까?')) return;

        try {
            await fetchAPI(`/question/${id}`, {
                method: 'DELETE',
                body: JSON.stringify({ password }),
            });
            window.location.hash = '#/questions';
        } catch (error) {
            alert(`삭제 실패: ${error.message}`);
        }
    }

    async function handleUpdateQuestion(e, id) {
        e.preventDefault();
        const form = e.target;
        const subject = form.elements.subject.value;
        const content = form.elements.content.value;
        const password = form.elements.password.value;

        if (!password) { alert('비밀번호를 입력하세요.'); return; }

        try {
            await fetchAPI(`/question/${id}`, {
                method: 'PUT',
                body: JSON.stringify({ subject, content, password }),
            });
            await router(); // 페이지 새로고침
        } catch (error) {
            alert(`수정 실패: ${error.message}`);
        }
    }

    // --- Answer (답변/대댓글) 핸들러 ---
    async function handleAddAnswer(e) {
        e.preventDefault();
        const form = e.target;
        const questionId = form.dataset.questionId;
        const parentId = form.dataset.parentId || null;
        const content = form.elements['answer-content'].value;
        const password = form.elements['answer-password'].value;

        if (!content || !password) { alert('내용과 비밀번호를 입력하세요.'); return; }

        try {
            await fetchAPI('/answer/', {
                method: 'POST',
                body: JSON.stringify({ question_id: questionId, parent_id: parentId, content, password }),
            });
            await router(); // 페이지 새로고침
        } catch (error) {
            alert(`답변 등록 실패: ${error.message}`);
        }
    }

    async function handleDeleteAnswer(e, id) {
        e.preventDefault();
        const password = e.target.elements.password.value;
        if (!password) { alert('비밀번호를 입력하세요.'); return; }

        if (!confirm('정말로 이 답변을 삭제하시겠습니까?')) return;

        try {
            await fetchAPI(`/answer/${id}`, {
                method: 'DELETE',
                body: JSON.stringify({ password }),
            });
            await router();
        } catch (error) {
            alert(`삭제 실패: ${error.message}`);
        }
    }

    async function handleUpdateAnswer(e, id) {
        e.preventDefault();
        const form = e.target;
        const content = form.elements.content.value;
        const password = form.elements.password.value;
        if (!password) { alert('비밀번호를 입력하세요.'); return; }

        try {
            await fetchAPI(`/answer/${id}`, {
                method: 'PUT',
                body: JSON.stringify({ content, password }),
            });
            await router();
        } catch (error) {
            alert(`수정 실패: ${error.message}`);
        }
    }

    /**
     * 답글 폼을 토글합니다.
     */
    function showReplyForm(answerId, questionId) {
        const container = document.getElementById(`reply-form-for-${answerId}`);
        if (container.innerHTML) {
            container.innerHTML = ''; // 폼 닫기
            return;
        }

        container.innerHTML = `
            <form class="reply-form" data-question-id="${questionId}" data-parent-id="${answerId}">
                <h4>대댓글 작성</h4>
                <div class="form-group">
                    <textarea name="answer-content" class="form-control" required rows="3"></textarea>
                </div>
                <div class="form-group">
                    <input type="password" name="answer-password" class="form-control" required placeholder="비밀번호">
                </div>
                <button type="submit" class="btn btn-primary btn-small">등록</button>
                <button type="button" class="btn btn-secondary btn-small btn-cancel-reply">취소</button>
            </form>
        `;

        container.querySelector('form').addEventListener('submit', handleAddAnswer);
        container.querySelector('.btn-cancel-reply').addEventListener('click', () => container.innerHTML = '');
    }

    /**
     * 9. 깊은 답글 동적 로딩 핸들러
     */
    async function handleLoadReplies(answerId) {
        const loadButton = document.querySelector(`#load-more-for-${answerId} button`);
        loadButton.textContent = '로딩 중...';
        loadButton.disabled = true;

        try {
            // 백엔드의 get_single_answer API 호출
            const answerData = await fetchAPI(`/answer/${answerId}`);

            const repliesContainer = document.getElementById(`replies-for-${answerId}`);
            repliesContainer.innerHTML = ''; // 기존 얕은 답글(이 있다면) 지우고 새로 로드

            if (answerData.replies && answerData.replies.length > 0) {
                answerData.replies.forEach(reply => {
                    repliesContainer.appendChild(createAnswerElement(reply));
                });
            } else {
                repliesContainer.innerHTML = '<p>답글이 없습니다.</p>';
            }

            loadButton.parentElement.innerHTML = ''; // '더보기' 버튼 제거

        } catch (error) {
            alert(`답글 로딩 실패: ${error.message}`);
            loadButton.textContent = '로딩 실패. 재시도';
            loadButton.disabled = false;
        }
    }


    // --- Admin 핸들러 ---
    async function handleAdminSoftDelete(event, itemType, id) {
        // (선택적) 이벤트 버블링 방지 (e.g. 질문 목록에서 바로 삭제 시)
        event.stopPropagation();
        event.preventDefault();

        if (!confirm(`[관리자 기능]\n\n'${itemType}' (ID: ${id}) 항목을 소프트 삭제(Soft Delete)합니다.\n\n사용자에게는 보이지 않게 되며, 관리자 페이지에서만 복구/영구삭제할 수 있습니다. 계속하시겠습니까?`)) {
            return;
        }

        try {
            await fetchAPI(`/admin/soft-delete/${itemType}/${id}`, {
                method: 'DELETE',
            });
            alert('관리자 권한으로 소프트 삭제되었습니다.\n목록을 새로고침합니다.');
            await router(); // 페이지 새로고침
        } catch (error) {
            // 이 API는 IP 기반으로 보호되므로, 권한이 없으면 403 Forbidden 에러 발생
            alert(`소프트 삭제 실패: ${error.message}\n\n(관리자 IP가 아니거나, 항목을 찾을 수 없습니다.)`);
        }
    }

    async function handleHardDelete(itemType, id) {
        if (!confirm(`[경고] '${itemType}' (ID: ${id}) 항목을 영구 삭제합니다.\n이 작업은 되돌릴 수 없습니다. 계속하시겠습니까?`)) {
            return;
        }
        try {
            await fetchAPI(`/admin/hard-delete/${itemType}/${id}`, { method: 'DELETE' });
            alert('영구 삭제되었습니다.');
            await renderAdminPage(); // 관리자 페이지 새로고침
        } catch (error) {
            alert(`영구 삭제 실패: ${error.message}`);
        }
    }
});
