# Prompt Management System

## Cấu trúc thư mục Prompts

```
prompts/
├── loan_analysis.txt              # Prompt cho phân tích hồ sơ vay
├── policy_check.txt               # Prompt cho kiểm tra chính sách
├── rag_response.txt               # Prompt cho trả lời câu hỏi RAG
└── data_extraction/
    ├── salary_employment.txt      # Trích xuất thông tin lương & hợp đồng
    ├── personal_information.txt    # Trích xuất thông tin cá nhân
    ├── asset_valuation.txt        # Trích xuất thông tin định giá tài sản
    └── credit_report.txt          # Trích xuất thông tin CIC/Credit Report
```

## Các Module Sử Dụng Prompts

### 1. **ai_analyzer.py** → `prompts/loan_analysis.txt`
```python
from modules.prompt_loader import load_prompt
from langchain_core.prompts import PromptTemplate

prompt_template = load_prompt("prompts/loan_analysis.txt")
self.prompt = PromptTemplate(
    input_variables=["income", "loan_amount", "credit_score"],
    template=prompt_template
)
```

### 2. **policy_checker.py** → `prompts/policy_check.txt`
```python
prompt_template = load_prompt("prompts/policy_check.txt")
self.policy_check_prompt = PromptTemplate(
    input_variables=["policy", "document_text", "document_category"],
    template=prompt_template
)
```

### 3. **data_extractor.py** → `prompts/data_extraction/*.txt`
```python
self.extraction_prompts = {
    "Salary & Employment Contract": PromptTemplate(
        input_variables=["document_text"],
        template=load_prompt("prompts/data_extraction/salary_employment.txt")
    ),
    "Personal Information": PromptTemplate(
        input_variables=["document_text"],
        template=load_prompt("prompts/data_extraction/personal_information.txt")
    ),
    # ... các category khác
}
```

### 4. **rag_engine.py** → `prompts/rag_response.txt`
```python
prompt_template = load_prompt("prompts/rag_response.txt")
prompt = PromptTemplate(
    input_variables=["context", "query"],
    template=prompt_template
)
```

## Utility: prompt_loader.py

```python
def load_prompt(prompt_file: str) -> str:
    """
    Load prompt template from file.
    
    Args:
        prompt_file (str): Path relative to project root
        
    Returns:
        str: Prompt content
    """
```

## Lợi Ích của Tách Prompt

✅ **Dễ bảo trì**: Prompts tách riêng dễ chỉnh sửa mà không cần sửa code  
✅ **Khái rõ ràng**: Tách biệt concerns giữa logic code và prompt templates  
✅ **Tái sử dụng**: Dễ dàng tái sử dụng prompts giống nhau trong nhiều module  
✅ **Quản lý phiên bản**: Dễ theo dõi thay đổi prompts trong Git  
✅ **Dễ test**: Có thể test prompts độc lập mà không cần chạy toàn bộ module  

## Cách Chỉnh Sửa Prompts

1. Mở file prompt cần chỉnh sửa từ thư mục `prompts/`
2. Thay đổi template text
3. Module sẽ tự động load prompt mới lần tiếp theo chạy (không cần restart nếu reload)

## Variables Có Sẵn Trong Prompts

### `loan_analysis.txt`
- `{income}` - Thu nhập hàng tháng
- `{loan_amount}` - Số tiền vay
- `{credit_score}` - Điểm tín dụng

### `policy_check.txt`
- `{policy}` - Nội dung chính sách từ loan_policy.txt
- `{document_text}` - Nội dung tài liệu
- `{document_category}` - Loại tài liệu

### `data_extraction/*.txt`
- `{document_text}` - Nội dung tài liệu

### `rag_response.txt`
- `{context}` - Văn bản context từ vector DB
- `{query}` - Câu hỏi của người dùng
