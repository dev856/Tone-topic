import streamlit as st
import gensim
from gensim import corpora, models
import re
import heapq
import whisper
import os
import shutil
import pandas as pd
#from annotated_text import annotated_text
#list of topics based on industries

insurance = ['actuary', 'claims', 'coverage', 'deductible', 'policyholder', 'premium', 'underwriter', 'risk assessment', 'insurable interest', 'loss ratio', 'reinsurance', 'actuarial tables', 'property damage', 'liability', 'flood insurance', 'term life insurance', 'whole life insurance', 'health insurance', 'auto insurance', 'homeowners insurance', 'marine insurance', 'crop insurance', 'catastrophe insurance', 'umbrella insurance', 'pet insurance', 'travel insurance', 'professional liability insurance', 'disability insurance', 'long-term care insurance', 'annuity', 'pension plan', 'group insurance', 'insurtech', 'insured', 'insurer', 'subrogation', 'adjuster', 'third-party administrator', 'excess and surplus lines', 'captives', 'workers compensation', 'insurance fraud', 'health savings account', 'health maintenance organization', 'preferred provider organization','annuitant', 'beneficiary', 'peril', 'actuarial modeling', 'catastrophe modeling', 'reinsurance treaty', 'facultative reinsurance', 'health maintenance organization', 'indemnity', 'reinsurance broker', 'risk management', 'self-insurance','surplus lines', 'policy limit', 'policy term']

finance = ['asset', 'liability', 'equity', 'capital', 'portfolio', 'dividend', 'financial statement', 'balance sheet', 'income statement', 'cash flow statement', 'statement of retained earnings', 'financial ratio', 'valuation', 'bond', 'stock', 'mutual fund', 'exchange-traded fund', 'hedge fund', 'private equity', 'venture capital', 'mergers and acquisitions', 'initial public offering', 'secondary market', 'primary market', 'securities', 'derivative', 'option', 'futures', 'forward contract', 'swaps', 'commodities', 'credit rating', 'credit score', 'credit report', 'credit bureau', 'credit history', 'credit limit', 'credit utilization', 'credit counseling', 'credit card', 'debit card', 'ATM', 'bankruptcy', 'foreclosure', 'debt consolidation', 'taxes', 'tax return', 'tax deduction', 'tax credit', 'tax bracket', 'taxable income','asset allocation', 'capital gain', 'dividend yield', 'financial planner', 'hedge fund manager', 'liquidity', 'market risk', 'price-to-earnings ratio', 'return on investment', 'shareholder equity', 'tax exemption', 'value investing', 'working capital']

banking_capital_markets = ['bank', 'credit union', 'savings and loan association', 'commercial bank', 'investment bank', 'retail bank', 'wholesale bank', 'online bank', 'mobile banking', 'checking account', 'savings account', 'money market account', 'certificate of deposit', 'loan', 'mortgage', 'home equity loan', 'line of credit', 'credit card', 'debit card', 'ATM', 'automated clearing house', 'wire transfer', 'ACH', 'SWIFT', 'international banking', 'foreign exchange', 'forex', 'currency exchange', 'central bank', 'Federal Reserve', 'interest rate', 'inflation', 'deflation', 'monetary policy', 'fiscal policy', 'quantitative easing', 'securities', 'stock', 'bond', 'mutual fund', 'exchange-traded fund', 'hedge fund', 'private equity', 'venture capital', 'investment management', 'portfolio management', 'wealth management', 'financial planning','asset-backed securities', 'central clearing counterparty', 'collateralized debt obligation', 'credit default swap', 'interest rate swap', 'investment grade', 'prime brokerage', 'prime rate', 'retail investor', 'securities lending', 'sovereign wealth fund', 'yield curve']

healthcare_life_sciences = ['medical device', 'pharmaceutical', 'biotechnology', 'clinical trial', 'FDA', 'healthcare provider', 'healthcare plan', 'healthcare insurance', 'patient', 'doctor', 'nurse', 'pharmacist', 'hospital', 'clinic', 'healthcare system', 'healthcare policy', 'public health', 'healthcare IT', 'electronic health record', 'telemedicine', 'personalized medicine', 'genomics', 'proteomics', 'clinical research', 'drug development', 'drug discovery', 'medicine', 'health','biomedical engineering', 'clinical pathway', 'healthcare reform', 'medical coding', 'medical imaging', 'patient-centered care', 'personalized healthcare', 'pharmaceutical research', 'public health policy', 'telehealth', 'wearable technology']

law = ['law', 'legal', 'attorney', 'lawyer', 'litigation', 'arbitration', 'dispute resolution', 'contract law', 'intellectual property', 'corporate law', 'labor law', 'tax law', 'real estate law', 'environmental law', 'criminal law', 'family law', 'immigration law', 'bankruptcy law','amicus curiae', 'case law', 'class action', 'legal precedent', 'litigation funding', 'pro bono', 'statutory law', 'trial advocacy', 'white-collar crime', 'legal brief', 'legal ethics', 'legal writing']

sports = ['sports', 'football', 'basketball', 'baseball', 'hockey', 'soccer', 'golf', 'tennis', 'olympics', 'athletics', 'coaching', 'sports management', 'sports medicine', 'sports psychology', 'sports broadcasting', 'sports journalism', 'esports', 'fitness','athletic training', 'competitive balance', 'sports analytics', 'sports sponsorship', 'sportsmanship', 'team chemistry', 'sports officiating', 'sports economics', 'sports nutrition', 'sports fandom', 'sports memorabilia']

media = ['media', 'entertainment', 'film', 'television', 'radio', 'music', 'news', 'journalism', 'publishing', 'public relations', 'advertising', 'marketing', 'social media', 'digital media', 'animation', 'graphic design', 'web design', 'video production','content creation', 'influencer marketing', 'media convergence', 'media literacy', 'native advertising', 'podcasting', 'streaming service', 'user-generated content', 'viral marketing', 'vlogging']

manufacturing = ['manufacturing', 'production', 'assembly', 'logistics', 'supply chain', 'quality control', 'lean manufacturing', 'six sigma', 'industrial engineering', 'process improvement', 'machinery', 'automation', 'aerospace', 'automotive', 'chemicals', 'construction materials', 'consumer goods', 'electronics', 'semiconductors','inventory management', 'just-in-time manufacturing', 'product lifecycle management', 'quality assurance', 'supply chain optimization', 'value stream mapping', 'additive manufacturing', 'robotics integration', 'industrial safety', 'sustainability practices']

automotive = ['automotive', 'cars', 'trucks', 'SUVs', 'electric vehicles', 'hybrid vehicles', 'autonomous vehicles', 'car manufacturing', 'automotive design', 'car dealerships', 'auto parts', 'vehicle maintenance', 'car rental', 'fleet management', 'telematics','connected vehicles', 'crash test', 'electric vehicle infrastructure', 'fuel efficiency', 'automotive engineering', 'automotive technology', 'aftermarket parts', 'automotive aftermarket', 'automotive safety', 'automotive trends']

telecom = ['telecom', 'telecommunications', 'wireless', 'networks', 'internet', 'broadband', 'fiber optics', '5G', 'telecom infrastructure', 'telecom equipment', 'VoIP', 'satellite communications', 'mobile devices', 'smartphones', 'telecom services', 'telecom regulation', 'telecom policy','network infrastructure', 'telecom operator', 'telecom regulation', 'telecom spectrum', 'telecom tower', 'broadband penetration', 'mobile network', 'telecom convergence', 'telecom ecosystem', 'telecom satellite']


information_technology = [
    "Artificial intelligence", "Machine learning", "Data Science", "Big Data", "Cloud Computing",
    "Cybersecurity", "Information security", "Network security", "Blockchain", "Cryptocurrency",
    "Internet of things", "IoT", "Web development", "Mobile development", "Frontend development",
    "Backend development", "Software engineering", "Software development", "Programming",
    "Database", "Data analytics", "Business intelligence", "DevOps", "Agile", "Scrum",
    "Product management", "Project management", "IT consulting", "IT service management", 
    "ERP", "CRM", "SaaS", "PaaS", "IaaS", "Virtualization", "Artificial reality", "AR", "Virtual reality",
    "VR", "Gaming", "E-commerce", "Digital marketing", "SEO", "SEM", "Content marketing",
    "Social media marketing", "User experience", "UX design", "UI design", "Cloud-native",
    "Microservices", "Serverless", "Containerization",'algorithm development', 'cloud security', 'data governance', 'distributed computing', 'edge computing', 'IT infrastructure', 'machine learning algorithms', 'quantum computing', 'software architecture', 'technology stack'
]
#mapping of the keywords with industry title
industries = {
    'Insurance': insurance,
    'Finance': finance,
    'Banking': banking_capital_markets,
    'Healthcare': healthcare_life_sciences,
    'Legal': law,
    'Sports': sports,
    'Media': media,
    'Manufacturing': manufacturing,
    'Automotive': automotive,
    'Telecom': telecom,
    'IT': information_technology
}


def label_to(text):
    # count the number of occurrences of each keyword in the text for each industry
    counts = {}
    for i, k in industries.items():
        count = sum([1 for i in k if re.search(r"\b{}\b".format(i), text, re.IGNORECASE)])
        counts[i] = count
    # Geting the top two industries based on their number of counts
    top_i = heapq.nlargest(3, counts, key=counts.get)
    # handling edge case
    if len(top_i) == 1:
        return top_i[0]
    else:
        return top_i



def topic_modeling(text_trans, num_topics=4, num_words=10):
    # Preprocessing the transcript text
    
    preprocessed_text = prepro_text(text_trans)

    # Here we are creating a dictionary of all unique words in the transcripts
    dictio = corpora.Dictionary(preprocessed_text)

    # Afte that we are converting  the preprocessed transcripts into a bag-of-words representation
    corpus = [dictio.doc2bow(text) for text in preprocessed_text]

    # here we are training an LDA model with the specified number of topics
    lda = models.LdaModel(corpus=corpus, id2word=dictio, num_topics=num_topics)

    # here we are extracting the most probable words for each topic
    topics = []
    for i, topic in lda.print_topics(-1, num_words=num_words):
        # Extract the top words for each topic and store in a list
        topic_w = [word.split('*')[1].replace('"', '').strip() for word in topic.split('+')]
        topics.append((f"Topic {i}", topic_w))
    return topics

def prepro_text(text):
    
    # This code simply tokenizes the text and removes stop words
    tokens = gensim.utils.simple_preprocess(text)
    stop_words = gensim.parsing.preprocessing.STOPWORDS
    preprocessed_text = [[token for token in tokens if token not in stop_words]]

    return preprocessed_text

st.set_page_config(layout="wide")

#here we are giveing option for selecting the input source
choice = st.sidebar.selectbox("Select the input file type", ["Text","CSV"])

if choice == "Text":
    
    st.subheader("Tone Topic: Topic Modeling and Labeling in the Streamlit Sea")

    # here we are creating the text area space which allows user to enter the paragraph which they want to label
    text = st.text_area("Enter the text below", height=250)

    if text is not None:

        if st.button("Submit"):
            col1, col2, col3 = st.columns([1,1,1])
            with col1:
                st.info("Below is the provided text")
                st.success(text)
            with col2:
                # Performing topic modeling on the transcripted text 
                #here we are calling the function topic_modeling 
                topics = topic_modeling(text)

                # Display the resulting topics in the app
                st.info("Topics")
                for topic in topics:
                    st.success(f"{topic[0]}: {', '.join(topic[1])}")
            with col3:
                st.info("Labeling")
                labeling_text = text
                industry = label_to(labeling_text)
                st.markdown("**Industry Wise Lebeling**")
                st.write(industry)
           
elif choice == "CSV":
    st.subheader("Topic Modeling and Labeling on CSV file using Streamlit")
    csv = st.file_uploader("Upload your CSV file", type=['csv'])
    if csv is not None:
        if st.button("Submit CSV File"):
            col1, col2 = st.columns([1,2])
            with col1:
                st.info("File uploaded")
                csv_f = csv.name
                with open(os.path.join(csv_f),"wb") as f: 
                    f.write(csv.getbuffer()) 
                print(csv_f)
                df = pd.read_csv(csv_f, encoding= 'unicode_escape')
                st.dataframe(df)
            with col2:
                data_list = df['Data'].tolist()
                industry_list = []
                for i in data_list:
                    industry = label_to(i)
                    industry_list.append(industry)
                df['Industry'] = industry_list
                st.info("Topic Labeling and Modleing")
                st.dataframe(df)
                
            