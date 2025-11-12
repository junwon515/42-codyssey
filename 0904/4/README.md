# 📋 Todo & Q&A 프로젝트 아키텍처 스터디 가이드

안녕하세요! 이 문서는 우리 (Todo & Q&A) 프로젝트에 적용된 **헥사고날 아키텍처(Hexagonal Architecture)** 와 관련 개념들을 공유하기 위해 작성되었습니다.

이 프로젝트의 목표는 단순히 기능을 '동작'하게 만드는 것을 넘어, 어떻게 하면 **유지보수하기 쉽고, 테스트하기 용이하며, 변화에 유연하게 대처**할 수 있는 애플리케이션을 만들 수 있을까에 대한 고민을 담는 것이었습니다.

## 1. 핵심 철학: 클린 아키텍처와 헥사고날 아키텍처

우리가 적용한 '헥사고날 아키텍처'는 '클린 아키텍처'의 철학을 구현하는 구체적인 패턴 중 하나입니다.

### 클린 아키텍처 (Clean Architecture)

"양파"처럼 계층화된 구조를 상상해 보세요. 클린 아키텍처의 핵심 규칙은 단 하나입니다.

> **"모든 의존성은 바깥에서 안쪽으로만 향해야 한다."**



* **가운데 (Domain):** 애플리케이션의 가장 핵심적인 비즈니스 로직과 규칙. **(e.g., `src/domain/models.py`)**
* **바깥쪽 (Infrastructure):** 데이터베이스, 웹 프레임워크(FastAPI), 외부 API 등 구체적인 기술. **(e.g., `src/infrastructure`)**

이 규칙을 지키면, 데이터베이스가 `SQLite`에서 `PostgreSQL`로 바뀌거나, `FastAPI`가 `Django`로 바뀌어도(극단적이지만) **핵심 비즈니스 로직(Domain)은 전혀 영향을 받지 않습니다.**

### 헥사고날 아키텍처 (Ports & Adapters)

클린 아키텍처의 "어떻게?"에 대한 답입니다. "육각형"의 안과 밖을 상상해 보세요.



* **안 (Inside):** 우리의 순수한 애플리케이션 로직. **(e.g., `src/domain`, `src/application/services.py`)**
* **밖 (Outside):** FastAPI, SQLAlchemy, Bcrypt 등 외부 세계의 모든 것.

이 둘을 어떻게 연결하고 분리할까요? 바로 **"포트(Ports)"** 와 **"어댑터(Adapters)"** 입니다.

* **포트 (Ports):**
    * 육각형의 "안쪽"에 정의된 **'인터페이스(추상화)'** 입니다.
    * "나는 이런 기능이 필요해"라고 명시만 할 뿐, '어떻게' 동작하는지는 모릅니다.
    * 우리 프로젝트의 `src/domain/ports.py`가 정확히 이 역할을 합니다. `TodoRepository`나 `PasswordManager`같은 인터페이스(Protocol)가 바로 '포트'입니다.

* **어댑터 (Adapters):**
    * 육각형의 "바깥쪽"에 정의된 **'구현체'** 입니다.
    * 이 '포트'에 꽂아서 실제로 동작하는 코드입니다.
    * **Input Adapters (입력 어댑터):** 외부에서 애플리케이션을 *호출*하는 어댑터.
        * e.g., `src/infrastructure/adapters_in/http_api.py` (FastAPI 라우터)
    * **Output Adapters (출력 어댑터):** 애플리케이션이 외부를 *호출*하는 어댑터.
        * e.g., `src/infrastructure/adapters_out/datebase/repos.py` (SQLAlchemy Repository 구현체)
        * e.g., `src/infrastructure/adapters_out/password_manager.py` (Bcrypt 구현체)

---

## 2. 프로젝트에 적용된 주요 개념

이 아키텍처를 구현하기 위해 여러 중요한 디자인 패턴과 원칙이 사용되었습니다.

### A. 의존성 역전 원칙 (DIP - Dependency Inversion Principle)

> **"구체적인 것(Infrastructure)이 추상적인 것(Domain)에 의존해야 한다."**

이것이 클린 아키텍처를 가능하게 하는 핵심 원동력입니다.



* **전통적인 방식:** `Service`가 `SqlAlchemyRepo`를 직접 import 하고 의존합니다. (`Service` → `SqlAlchemyRepo`)
* **DIP 적용 (우리 프로젝트):**
    1.  `Domain` 레이어에 `TodoRepository`(인터페이스)라는 '포트'를 정의합니다.
    2.  `Application` 레이어의 `TodoService`는 추상적인 `TodoRepository`에만 의존합니다. (`TodoService` → `TodoRepository`)
    3.  `Infrastructure` 레이어의 `SqlAlchemyTodoRepository`가 `TodoRepository`를 *구현*합니다. (`SqlAlchemyTodoRepository` → `TodoRepository`)

결과적으로 의존성의 방향이 `Infrastructure` → `Domain`으로 "역전"되었습니다.

그럼 `TodoService`는 어떻게 실제 `SqlAlchemyTodoRepository`를 만나게 될까요? 바로 `src/infrastructure/core/dependencies.py` 파일에서 FastAPI의 `Depends`를 통해 런타임에 "주입(Dependency Injection)"됩니다.

### B. DTO - 도메인 엔티티 - DAO의 분리

이 프로젝트는 데이터 객체를 세 가지 역할로 명확하게 분리했습니다. 이는 보일러플레이트가 늘어나는 단점이 있지만, 각 계층의 관심사를 분리하는 데 매우 중요합니다.



1.  **DTO (Data Transfer Object)**
    * **역할:** 외부(e.g., API)와의 데이터 교환.
    * **특징:** Pydantic 모델을 사용. API 명세(Request/Response)에 사용됩니다. IP 마스킹 등 '표현'을 위한 로직이 포함될 수 있습니다.
    * **파일:** `src/infrastructure/adapters_in/dtos.py` (e.g., `TodoCreateRequest`, `TodoViewResponse`)

2.  **도메인 엔티티 (Domain Entity / Model)**
    * **역할:** **핵심 비즈니스 로직과 상태를 캡슐화.**
    * **특징:** 순수한 Python `dataclass`로 작성. `complete()`, `update()`처럼 비즈니스 '행위'를 메서드로 가집니다. DB나 API에 대해 아무것도 모릅니다.
    * **파일:** `src/domain/models.py` (e.g., `Todo`, `Question`)

3.  **DAO (Data Access Object)**
    * **역할:** 데이터베이스 스키마와의 1:1 매핑.
    * **특징:** `SQLAlchemy`의 `Base`를 상속받은 테이블 모델. DB의 컬럼, 타입, 관계를 정의합니다.
    * **파일:** `src/infrastructure/adapters_out/datebase/daos.py` (e.g., `TodoTable`, `QuestionTable`)

이 세 객체 간의 변환은 `src/infrastructure/adapters_out/datebase/mappers.py`에서 명시적으로 이루어집니다.

### C. Unit of Work (UoW) 패턴

* **역할:** 비즈니스 트랜잭션 관리.
* `Application` 레이어의 서비스(`services.py`)가 "언제" DB 트랜잭션을 시작하고, 커밋(commit)하거나 롤백(rollback)할지 결정합니다.
* `src/infrastructure/adapters_out/datebase/uow.py`의 `SqlAlchemyUnitOfWork` 클래스가 `AsyncSession`의 생명주기(`__aenter__`, `__aexit__`)를 관리하며 이 패턴을 구현합니다.
* `TodoService`는 `uow.commit()`을 호출할 뿐, 그것이 `SQLAlchemy` 세션을 커밋하는 것인지는 알지 못합니다. (DIP)

---

## 3. 도메인 주도 설계 (DDD) - 실용적인 접근 방식

이 프로젝트의 아키텍처는 DDD의 영향을 강하게 받았습니다. 하지만 모든 규칙을 맹목적으로 따르기보다 현실적인 절충안을 선택했습니다.

### A. 도메인 주도 설계(DDD)란 무엇인가?

DDD(Domain-Driven Design)는 **"복잡한 비즈니스 로직"** 을 효과적으로 모델링하기 위한 소프트웨어 개발 접근 방식입니다. 핵심 목표는 **코드와 비즈니스(도메인) 간의 격차를 줄이는 것**입니다.

이를 위해 '엔티티', '값 객체', '리포지토리' 등 다양한 전술적 패턴을 사용하며, 그중 가장 중요한 개념 중 하나가 **'애그리거트(Aggregate)'** 입니다.

### B. 이 프로젝트에 적용된 DDD ("DDD 맛보기")

우리 프로젝트는 DDD의 핵심적인 전술적 패턴을 성공적으로 적용했습니다.

1.  **풍부한 도메인 모델 (Rich Domain Model):**
    * 엔티티가 단순한 데이터 덩어리가 아닙니다. `src/domain/models.py`의 `Todo` 엔티티는 `complete()`, `uncomplete()`, `update()`처럼 스스로의 상태를 변경하는 **행위(Behavior)** 를 캡슐화하고 있습니다.
2.  **리포지토리 패턴 (Repository Pattern):**
    * `src/domain/ports.py`에 리포지토리 인터페이스(포트)를 정의하여, 도메인이 특정 데이터베이스 기술(e.g., SQLAlchemy)에 종속되지 않도록 분리했습니다.

### C. 왜 "엄격한(Strict) DDD"는 적용하지 않았는가?

'엄격한 DDD'를 따른다면 **'애그리거트(Aggregate)'** 규칙을 강제해야 합니다.

* **애그리거트(Aggregate)란?**
    * '하나의 단위'로 취급되어야 하는 연관 객체들의 묶음입니다.
    * **(예시)** `User` 엔티티가 `UserProfile`, `UserCredential`, `SocialAccount` 같은 여러 세부 엔티티를 소유하는 경우, 이 모든 것을 묶어 `User` 애그리거트라고 부릅니다. `User`는 이 묶음의 '루트(Root)'가 됩니다.
    * **(우리 프로젝트)** `Question`과 `Answer`는 명백히 하나의 논리적인 애그리거트이며, `Question`이 그 '루트'입니다.

* **엄격한 DDD의 규칙:**
    * 애그리거트 외부에서는 **오직 '루트 엔티티'(e.g., `User` 또는 `Question`)의 리포지토리만 접근**할 수 있습니다.
    * `SocialAccount`를 변경하고 싶다면, `SocialAccount` 리포지토리에 접근하는 것이 아니라, `User` 루트를 가져와서 `user.update_social_account(...)` 같은 메서드를 호출해야 합니다.

**이 프로젝트가 엄격한 DDD가 아닌 이유:**

`src/application/services.py`의 `AnswerService`를 보면, `Question` 루트를 통하지 않고 `self.uow.answers.add(new_answer)`처럼 `Answer` 리포지토리에 직접 접근하여 데이터를 추가합니다. 이는 애그리거트 루트 규칙을 **의도적으로 위반**한 것입니다.

### D. 현실적인 트레이드오프: 왜 지금 방식이 더 나을까? 🤔

그렇다면 왜 애그리거트 규칙을 따르지 않았을까요? **"실용성"** 과 **"성능"** 때문입니다.

1.  **치명적인 성능 문제 (Performance Issue)**
    * 만약 '엄격한 DDD'를 따라 `Answer`를 추가하기 위해 `Question` 루트를 로드해야 한다고 가정해 봅시다.
    * 만약 어떤 `Question`에 `Answer`가 10,000개 달려있다면, 고작 답변 하나를 추가하기 위해 **불필요한 10,000개의 답변 객체를 모두 메모리에 로드**해야 할 수도 있습니다. 이는 심각한 성능 저하를 유발합니다.

2.  **낮은 도메인 복잡도 (Low Domain Complexity)**
    * 우리 프로젝트의 도메인(Todo, Q&A)은 솔직히 말해 "매우 복잡"하지 않습니다.
    * `Answer`를 추가할 때 `Question`의 다른 상태(e.g., `Question`의 제목)를 변경해야 하는 복잡한 비즈니스 규칙이 없습니다.
    * 현재 `AnswerService`가 `Question`의 존재 여부만 확인하는 방식은 로직이 명확하고, 효율적이며, 충분히 안전합니다.

**결론:** 엄격한 DDD의 애그리거트 패턴은 데이터 일관성을 매우 강하게 보장하지만, 우리 프로젝트의 요구사항에 비해 **과도한 엔지니어링(Over-engineering)** 이며 성능상 불이익이 더 큽니다.

### E. "DDD는 안 좋은가?" - 실무적 관점: MSA와 EDA

그렇다면 "엄격한 DDD를 안 하는 게 좋다"는 뜻일까요? 혹은 DDD가 안 좋은 걸까요?

**그렇지 않습니다. DDD는 도구를 사용하는 하나의 방식일 뿐입니다.**

실무에서는 우리 프로젝트보다 더 나아가, **마이크로서비스 아키텍처(MSA)** 를 도입하는 경우가 많습니다.

예를 들어, `Answer` 관련 처리가 `Question`보다 훨씬 많아서 서버 확장이 필요하다면, `Question` 도메인과 `Answer` 도메인을 **물리적으로 분리된 별개의 마이크로서비스로** 나눌 수 있습니다.

* 이 경우, 두 서비스는 **데이터베이스도 분리**됩니다.
* `Question`과 `Answer`는 더 이상 단일 트랜잭션(e.S., 우리 프로젝트의 UoW)으로 묶일 수 없습니다.
* 대신, 두 도메인은 **이벤트 기반 아키텍처(EDA)** 를 통해 **느슨하게 결합(Loose Coupling)** 됩니다.
* (예시) `Question`이 삭제되면, `Question` 서비스는 `QuestionDeletedEvent`라는 이벤트를 발행(publish)합니다. `Answer` 서비스는 이 이벤트를 구독(subscribe)하고 있다가, 이벤트를 받으면 "아, 내가 가진 답변들을 지워야겠구나"라고 인지하고 스스로의 DB에서 관련 답변을 삭제합니다. (이러한 트랜잭션 흐름을 **사가 패턴(Saga Pattern)** 이라고도 부릅니다.)

**요점:** DDD의 애그리거트 패턴은 강력하지만, 확장성(Scalability) 등 다른 요인으로 인해 논리적인 도메인을 물리적으로 분리(MSA)하기도 합니다. 이때는 EDA를 통해 약한 결합을 유지합니다.

**결국, DDD는 '법'이 아니라 '도구 상자'이며, 우리는 그중 '풍부한 엔티티', '리포지토리' 등 우리에게 필요한 도구만 현명하게 선택해 사용한 것입니다.**

---

## 4. 장점: 왜 이렇게까지 했을까? 🚀

1.  **최고의 테스트 용이성 (Testability):**
    * `Application` 레이어(`services.py`)를 테스트할 때, 실제 DB가 필요 없습니다. `domain/ports.py`의 인터페이스를 따르는 '가짜(Fake) UoW'와 '가짜 Repository'를 메모리에 만들어 주입하면 됩니다. 이는 매우 빠르고 격리된 테스트를 가능하게 합니다.

2.  **유연성 및 유지보수성 (Flexibility):**
    * 비밀번호 해싱을 `bcrypt`에서 `argon2`로 바꾸고 싶나요? `src/infrastructure/adapters_out/password_manager.py` 파일만 새로 구현하고 `dependencies.py`에서 교체해주면 `Domain`이나 `Application` 로직은 단 한 줄도 수정할 필요가 없습니다.

3.  **명확성 (Clarity):**
    * 프로젝트를 처음 보는 사람도 `src/domain/models.py`와 `src/domain/ports.py`만 읽으면 이 앱이 어떤 비즈니스 로직을 가졌는지 90% 이상 파악할 수 있습니다. `FastAPI`나 `SQLAlchemy`의 복잡한 코드에 파묻히지 않아도 됩니다.

## 5. 현실적인 고민과 단점 😥

물론 이 아키텍처가 만병통치약은 아닙니다.

1.  **보일러플레이트 코드 증가:**
    * 가장 큰 단점입니다. 간단한 `Todo` 기능 하나를 추가하기 위해 `DTO`, `Domain Model`, `DAO`, `Mapper`, `Repository` 인터페이스와 구현체까지... 많은 파일을 만들어야 합니다. 작은 프로젝트나 프로토타입에는 과할 수 있습니다.

2.  **매퍼(Mapper) 작성의 번거로움:**
    * `Domain Model`과 `DAO`를 분리하면서, 이 둘을 변환해주는 `mappers.py` 코드를 계속 작성해야 합니다.
    * (현실적 고민) "그냥 SQLAlchemy 모델(DAO)을 도메인 엔티티로 쓰면 안 되나?"라는 유혹이 계속 듭니다. (하지만 그렇게 하면 도메인이 DB 기술에 종속됩니다.)

3.  **학습 곡선 (Learning Curve):**
    * `DIP`, '포트', '어댑터' 같은 추상적인 개념에 익숙해지는 데 시간이 걸립니다.

## 결론

헥사고날 아키텍처는 **"빠른 개발"** 보다는 **"지속 가능한 개발"** 을 위한 투자입니다.

초기 설정과 보일러플레이트는 많지만, 프로젝트가 복잡해지고 요구사항이 계속 변경될수록, 이 견고한 "성벽(Hexagon)"이 우리의 핵심 비즈니스 로직을 외부의 변화로부터 안전하게 지켜줄 것입니다.

이 프로젝트가 여러분이 아키텍처를 고민하는 데 좋은 참고 자료가 되길 바랍니다!
