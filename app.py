"""
AI Loan Analyzer - Main Application
This module serves as the entry point for the AI-powered loan analysis system.
"""

import streamlit as st
from modules.ai_analyzer import analyze_loan
from modules.document_parser import DocumentParser
from modules.rag_engine import RAGEngine
from modules.data_extractor import DataExtractor
from modules.policy_checker import PolicyChecker
from modules import rule_engine


# Initialize session state
if "rag_engine" not in st.session_state:
    st.session_state.rag_engine = RAGEngine()
if "policy_checker" not in st.session_state:
    st.session_state.policy_checker = PolicyChecker()
if "documents_indexed" not in st.session_state:
    st.session_state.documents_indexed = False
if "data_extractor" not in st.session_state:
    st.session_state.data_extractor = DataExtractor()


st.title("AI Loan Application Analyzer - Made by Thơ Béo")

# Initialize components
parser = DocumentParser()
rag_engine = st.session_state.rag_engine
data_extractor = st.session_state.data_extractor
policy_checker = st.session_state.policy_checker

st.subheader("📋 Loan Application Form")

# Row 1: Personal Information
col1, col2, col3 = st.columns(3)

with col1:
    full_name = st.text_input(
        "Full Name *",
        placeholder="Enter your full name",
        help="Required: Your full legal name"
    )

with col2:
    date_of_birth = st.date_input(
        "Date of Birth *",
        help="Required: Select your date of birth"
    )

with col3:
    gender = st.selectbox(
        "Gender *",
        options=["", "Male", "Female", "Other"],
        help="Required: Select your gender"
    )

# Row 2: Financial Information
col1, col2, col3 = st.columns(3)

with col1:
    monthly_income = st.number_input(
        "Monthly Income *",
        min_value=0.0,
        step=100.0,
        help="Required: Enter monthly income in USD"
    )

with col2:
    loan_amount = st.number_input(
        "Loan Amount *",
        min_value=0.0,
        step=1000.0,
        help="Required: Enter desired loan amount in USD"
    )

with col3:
    loan_term_months = st.number_input(
        "Loan Term (Months) *",
        min_value=1,
        max_value=360,
        step=1,
        value=60,
        help="Required: Loan repayment period in months"
    )

# Row 3: Credit and Debt Information
col1, col2, col3 = st.columns(3)

with col1:
    credit_score = st.number_input(
        "Credit Score *",
        min_value=300.0,
        max_value=850.0,
        step=1.0,
        value=650.0,
        help="Required: Enter credit score (300-850)"
    )

with col2:
    monthly_debt_payment = st.number_input(
        "Monthly Debt Payment *",
        min_value=0.0,
        step=50.0,
        help="Required: Your monthly debt payments in USD"
    )

with col3:
    property_value = st.number_input(
        "Property Value *",
        min_value=0.0,
        step=1000.0,
        help="Required: Property collateral value in USD"
    )

# Row 4: Employment Information
col1, col2 = st.columns(2)

with col1:
    employment_years = st.number_input(
        "Employment Years *",
        min_value=0.0,
        max_value=70.0,
        step=0.5,
        help="Required: Years at current employment"
    )

# File uploader for multiple files by category
st.subheader("📄 Upload Loan Documents")
st.write("Supported formats: PDF, PNG, JPG, JPEG, TXT, DOC, DOCX")

# Document categories
doc_categories = {
    "💼 Thông tin lương & Hợp đồng lao động": "Salary & Employment Contract",
    "👤 Thông tin cá nhân": "Personal Information",
    "🏠 Thông tin định giá tài sản": "Asset Valuation Information",
    "📊 Thông tin CIC/Credit report": "CIC/Credit Report"
}

uploaded_files_by_category = {}

for category_display, category_key in doc_categories.items():
    uploaded_files_by_category[category_key] = st.file_uploader(
        category_display + " *",
        type=["pdf", "png", "jpg", "jpeg", "txt", "doc", "docx"],
        accept_multiple_files=True,
        help=f"Required: Upload at least one document for {category_display}",
        key=f"uploader_{category_key}"
    )

# Collect all uploaded files
all_uploaded_files = []
for category_key, files in uploaded_files_by_category.items():
    if files:
        for file in files:
            all_uploaded_files.append((file, category_key))

# Analyze button
if st.button("📊 Analyze Loan", use_container_width=True):
    # Validate required fields
    errors = []
    
    if not full_name or full_name.strip() == "":
        errors.append("Full Name is required")
    if not gender or gender == "":
        errors.append("Gender is required")
    if monthly_income <= 0:
        errors.append("Monthly Income must be greater than 0")
    if loan_amount <= 0:
        errors.append("Loan Amount must be greater than 0")
    if loan_term_months <= 0:
        errors.append("Loan Term must be greater than 0")
    if credit_score < 300 or credit_score > 850:
        errors.append("Credit Score must be between 300 and 850")
    if monthly_debt_payment < 0:
        errors.append("Monthly Debt Payment cannot be negative")
    if property_value < 0:
        errors.append("Property Value cannot be negative")
    if employment_years < 0:
        errors.append("Employment Years cannot be negative")
    if not all_uploaded_files:
        errors.append("At least one document must be uploaded in each category")
    
    if errors:
        st.error("❌ Please fix the following errors:")
        for error in errors:
            st.write(f"• {error}")
    else:
        # Parse all documents
        st.subheader("📝 Extracted Documents")
        
        extracted_texts = []
        document_names = []
        document_categories = []
        extracted_data_list = []
        
        for uploaded_file, category in all_uploaded_files:
            st.write(f"**{uploaded_file.name}** ({category})")
            
            # Read file content
            file_content = uploaded_file.read()
            
            # Parse document
            with st.spinner(f"Parsing {uploaded_file.name}..."):
                result = parser.parse_document(file_content, uploaded_file.name)
            
            # Display parsed content
            if "error" in result:
                st.error(f"❌ Error parsing {uploaded_file.name}: {result['error']}")
            else:
                extracted_text = result.get("text", "")
                st.text_area(
                    f"Content ({uploaded_file.name})",
                    extracted_text,
                    height=150,
                    disabled=True,
                    key=f"extracted_{uploaded_file.name}"
                )
                extracted_texts.append(extracted_text)
                document_names.append(uploaded_file.name)
                document_categories.append(category)
                
                # Extract structured data using category-specific prompt
                with st.spinner(f"Extracting structured data from {uploaded_file.name}..."):
                    extracted_data = data_extractor.extract_data(extracted_text, category)
                    extracted_data_list.append(extracted_data)
                    
                    # Display extracted data
                    if extracted_data.get("success"):
                        with st.expander(f"📊 Structured Data - {uploaded_file.name}"):
                            st.json(extracted_data.get("data", {}))
                    else:
                        st.warning(f"⚠️ Could not extract structured data: {extracted_data.get('error')}")
                
                # Check policy compliance
                with st.spinner(f"Checking policy compliance for {uploaded_file.name}..."):
                    policy_result = policy_checker.check_compliance(extracted_text, category)
                    
                    # Display violations
                    if policy_result.get("success"):
                        violations = policy_result.get("data", {}).get("violations", [])
                        if violations:
                            st.error(f"🚨 Policy Violations Found in {uploaded_file.name}")
                            with st.expander(f"📋 Violations Details - {uploaded_file.name}"):
                                for i, violation in enumerate(violations, 1):
                                    severity = violation.get("severity", "medium").upper()
                                    severity_emoji = {"LOW": "🟡", "MEDIUM": "🟠", "HIGH": "🔴"}.get(severity, "⚠️")
                                    
                                    st.markdown(f"{severity_emoji} **Violation {i}: {violation.get('policy_name', 'Unknown Policy')}**")
                                    st.write(f"**Detail:** {violation.get('violation_detail', '')}")
                                    st.write(f"**Policy Requirement:** {violation.get('policy_requirement', '')}")
                                    st.write(f"**Evidence from Document:** {violation.get('document_evidence', '')}")
                                    st.write(f"**Severity:** {severity}")
                                    st.divider()
                        else:
                            st.success(f"✅ Policy Compliant - {uploaded_file.name}")
                    else:
                        st.warning(f"⚠️ Could not check policy compliance: {policy_result.get('error')}")
        
        # Add documents to vector database (Chroma)
        if extracted_texts:
            with st.spinner("🔄 Indexing documents to vector database..."):
                try:
                    metadatas = [
                        {"source": name, "category": cat} 
                        for name, cat in zip(document_names, document_categories)
                    ]
                    rag_engine.add_documents(extracted_texts, metadatas)
                    rag_engine.index_documents()
                    st.session_state.documents_indexed = True
                    
                    # Check if vector DB is available
                    collection_info = rag_engine.get_collection_info()
                    if collection_info.get("vector_db_available", False):
                        st.success("✅ Documents indexed to Chroma vector database")
                    else:
                        st.warning("⚠️ Documents cached (Vector DB unavailable). Search features limited.")
                        st.info("💡 To enable vector search, ensure internet connection to OpenRouter API.")
                except Exception as e:
                    error_msg = str(e)
                    if "getaddrinfo failed" in error_msg or "Failed to resolve" in error_msg:
                        st.warning("⚠️ Network error: Cannot connect to vector database.")
                        st.info("📝 Documents saved to memory. Vector search features unavailable.")
                        st.session_state.documents_indexed = True
                    else:
                        st.error(f"❌ Error indexing documents: {error_msg}")
        
        # Create data dictionary with all applicant information
        data = {
            "full_name": full_name,
            "date_of_birth": str(date_of_birth),
            "gender": gender,
            "monthly_income": monthly_income,
            "loan_amount": loan_amount,
            "loan_term_months": loan_term_months,
            "credit_score": credit_score,
            "monthly_debt_payment": monthly_debt_payment,
            "property_value": property_value,
            "employment_years": employment_years
        }
        
        # ========== SEQUENTIAL DECISION-MAKING PROCESS ==========
        st.subheader("📋 Loan Decision Analysis")
        
        # STEP 1: Policy Checker - Check policy compliance
        st.write("**Step 1: Policy Compliance Check** 🚨")
        policy_violations = []
        
        for extracted_text, document_category in zip(extracted_texts, document_categories):
            policy_result = policy_checker.check_compliance(extracted_text, document_category)
            if policy_result.get("success"):
                violations = policy_result.get("data", {}).get("violations", [])
                if violations:
                    policy_violations.extend(violations)
        
        if policy_violations:
            st.warning(f"⚠️ Found {len(policy_violations)} policy violations:")
            for violation in policy_violations:
                severity = violation.get("severity", "medium").upper()
                severity_emoji = {"LOW": "🟡", "MEDIUM": "🟠", "HIGH": "🔴"}.get(severity, "⚠️")
                st.write(f"{severity_emoji} {violation.get('policy_name')}: {violation.get('violation_detail')}")
        else:
            st.success("✅ All documents comply with policies")
        
        st.divider()
        
        # STEP 2: Rule Engine - Evaluate loan based on business rules
        st.write("**Step 2: Risk Assessment (Rule Engine)** 📊")
        
        with st.spinner("Evaluating loan based on business rules..."):
            rule_evaluation = rule_engine.evaluate_loan(data)
            
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Credit Risk", rule_evaluation.get("credit_risk", "N/A"))
            with col2:
                dti_ratio = rule_evaluation.get("dti_ratio", 0)
                st.metric("Debt-to-Income", f"{dti_ratio:.2f}")
            with col3:
                st.metric("Employment Status", rule_evaluation.get("employment_status", "N/A"))
            with col4:
                ltv = rule_evaluation.get("loan_to_value_ratio", 0)
                st.metric("LTV Ratio", f"{ltv:.1f}%")
        
        st.divider()
        
        # STEP 3: RAG Engine - Retrieve context from documents for additional insights
        st.write("**Step 3: Document Context Retrieval (RAG)** 📚")
        
        rag_context = None
        if st.session_state.documents_indexed:
            with st.spinner("Retrieving relevant document context..."):
                # Generate a query based on applicant profile
                search_query = f"employment history income assets credit information for {full_name}"
                try:
                    rag_context = rag_engine.retrieve_context(search_query, top_k=3)
                    if rag_context:
                        st.success(f"✅ Retrieved {len(rag_context)} relevant document sections")
                        with st.expander("📄 Retrieved Document Context"):
                            for i, doc in enumerate(rag_context, 1):
                                st.write(f"**Context {i}:**")
                                st.text(doc.page_content[:500] + "..." if len(doc.page_content) > 500 else doc.page_content)
                    else:
                        st.info("ℹ️ No relevant context found in documents")
                except Exception as e:
                    st.warning(f"⚠️ Could not retrieve context: {str(e)}")
        else:
            st.info("ℹ️ Documents not indexed for retrieval")
        
        st.divider()
        
        # FINAL DECISION: Generate recommendation based on all factors
        st.write("**Final Recommendation** 🎯")
        
        with st.spinner("Generating final decision..."):
            result = analyze_loan(data)
        
        # Display comprehensive results
        st.subheader("🤖 AI Analysis Result")
        st.write(result)
        
        # Summary Card
        st.info(f"""
        **Loan Application Summary:**
        - Applicant: {full_name}
        - Requested Amount: ${loan_amount:,.2f}
        - Policy Violations: {len(policy_violations)} found
        - Credit Risk Level: {rule_evaluation.get("credit_risk")}
        - DTI Status: {rule_evaluation.get("dti_status")}
        - Employment: {rule_evaluation.get("employment_status")}
        """)
        
        st.divider()
        
        # Display document analysis summary
        st.subheader("📊 Document Analysis Summary")
        
        # Count documents by category
        category_counts = {}
        for _, category in all_uploaded_files:
            category_counts[category] = category_counts.get(category, 0) + 1
        
        col1, col2, col3, col4 = st.columns(4)
        for (cat_display, cat_key), col in zip(doc_categories.items(), [col1, col2, col3, col4]):
            with col:
                count = category_counts.get(cat_key, 0)
                st.metric(cat_display.split(" ", 1)[1], count)
        
        # Show collection info
        collection_info = rag_engine.get_collection_info()
        st.metric("Total Documents in Vector DB", collection_info.get("total_documents", 0))
        
        st.success("✅ Loan analysis completed successfully!")


# Document Search Section
if st.session_state.documents_indexed:
    st.divider()
    st.subheader("🔍 Search Documents")
    st.write("Tìm kiếm thông tin từ các tài liệu đã upload")
    
    search_query = st.text_input("Nhập từ khóa tìm kiếm", placeholder='Ví dụ: "lịch sử việc làm", "thu nhập", "địa chỉ"')
    
    if search_query:
        with st.spinner("Searching documents..."):
            try:
                # Use RAG to retrieve context without full AI response
                context_results = rag_engine.retrieve_context(search_query, top_k=5)
                
                if context_results:
                    st.success(f"✅ Tìm thấy {len(context_results)} kết quả phù hợp")
                    
                    for i, doc in enumerate(context_results, 1):
                        # Extract metadata
                        metadata = doc.metadata if hasattr(doc, 'metadata') else {}
                        source = metadata.get('source', 'Unknown document')
                        category = metadata.get('category', 'Unknown category')
                        
                        with st.expander(f"📄 Kết quả {i} - {source} ({category})"):
                            st.write(doc.page_content)
                else:
                    st.info("ℹ️ Không tìm thấy kết quả phù hợp")
                
            except Exception as e:
                st.error(f"❌ Lỗi tìm kiếm: {str(e)}")
