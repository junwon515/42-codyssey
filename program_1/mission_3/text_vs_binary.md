### **텍스트 파일과 이진 파일의 차이점 및 장단점**

파일은 크게 **텍스트 파일 (Text File)**과 **이진 파일 (Binary File)**로 나눌 수 있습니다.  

## **1. 텍스트 파일 (Text File)**
**형식:** 사람이 읽을 수 있는 문자로 저장됨 (예: `.txt`, `.csv`, `.html`, `.json` 등)  
**저장 방식:** ASCII 또는 UTF-8 같은 문자 인코딩을 사용하여 데이터를 저장  

### **장점**
- ✅ **가독성** – 사람이 직접 읽고 편집 가능  
- ✅ **범용성** – 다양한 운영체제 및 프로그램에서 쉽게 접근 가능  
- ✅ **버전 관리 용이** – Git과 같은 버전 관리 시스템에서 변경 사항을 쉽게 추적 가능  

### **단점**
- ❌ **저장 공간 비효율** – 숫자나 바이너리 데이터를 문자로 변환하여 저장하므로 크기가 커질 수 있음  
- ❌ **처리 속도 느림** – 숫자를 변환해야 하므로 연산 속도가 느려짐  
- ❌ **데이터 무결성 부족** – 줄 바꿈, 공백 등의 변형이 발생할 수 있어 데이터 손상 가능성이 있음  

---

## **2. 이진 파일 (Binary File)**
**형식:** 사람이 직접 읽을 수 없는 바이너리(2진수) 데이터로 저장됨 (예: `.exe`, `.jpg`, `.mp3`, `.dat` 등)  
**저장 방식:** 데이터를 그대로 2진수 형태로 저장  

### **장점**
- ✅ **저장 공간 효율성** – 숫자나 복잡한 데이터를 그대로 저장하므로 크기가 작음  
- ✅ **빠른 처리 속도** – 변환 과정 없이 직접 읽고 쓸 수 있어 속도가 빠름  
- ✅ **데이터 정확성 보장** – 줄 바꿈이나 공백 등의 변형 없이 원본 그대로 유지 가능  

### **단점**
- ❌ **가독성 부족** – 사람이 직접 읽거나 편집할 수 없음  
- ❌ **이식성 문제** – 운영체제나 프로그램에 따라 다르게 해석될 수 있음  
- ❌ **수정 어려움** – 특정 데이터를 변경하려면 별도의 프로그램이 필요  

---

### **📌 요약**
| 구분 | 텍스트 파일 | 이진 파일 |
|------|------------|------------|
| **형태** | 사람이 읽을 수 있는 문자 | 2진수 데이터 |
| **저장 방식** | ASCII, UTF-8 등 문자 인코딩 | 2진수로 직접 저장 |
| **파일 크기** | 비교적 큼 | 비교적 작음 |
| **처리 속도** | 느림 | 빠름 |
| **가독성** | 높음 (메모장 등에서 열림) | 낮음 (전용 프로그램 필요) |
| **데이터 무결성** | 낮음 (줄 바꿈, 공백 등 변형 가능) | 높음 (데이터 손상 적음) |

✅ **텍스트 파일**은 사람이 직접 읽고 수정해야 할 경우 유리  
✅ **이진 파일**은 성능이 중요하거나 데이터 크기를 줄여야 할 경우 유리  

어떤 파일 형식을 사용할지는 **목적**과 **사용 환경**에 따라 결정하면 됩니다! 😊

