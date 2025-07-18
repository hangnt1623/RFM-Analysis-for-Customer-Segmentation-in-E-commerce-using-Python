# -*- coding: utf-8 -*-
"""[Ver 2] Nguyen_Thuy_Hang_RFM_analysis_project.ipynb

Automatically generated by Colab.

Original file is located at
    https://colab.research.google.com/drive/1nJwZEWznfisHolCDQ8m_nUod6R40sYRn

#**Import dataset & libraries**
"""

from google.colab import drive
drive.mount('/content/drive')

path = '/content/drive/MyDrive/da/Python/Project3_ThuyHang_Python/ecommerce_retail.xlxs'

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import os
import warnings
warnings.filterwarnings('ignore')

xls = pd.ExcelFile('/content/drive/MyDrive/da/Python/Project3_ThuyHang_Python/ecommerce_retail.xlsx')

ecommerce_retail = xls.parse(sheet_name='ecommerce retail')
segmentation = xls.parse(sheet_name='Segmentation')

!pip install ydata-profiling

from ydata_profiling import ProfileReport

"""#**CONTEXT & PROBLEM**
 **1. Context**

SuperStore is a global retail company with a large customer base. As the Christmas and New Year holidays approach, the Marketing department plans to launch customer appreciation and loyalty campaigns. Given the scale of the data, traditional manual segmentation is no longer feasible.

 **2. Problem Understanding**

 The company needs to segment customers to run targeted marketing campaigns, but the growing volume of customer data makes manual methods like Excel ineffective. To address this,  Marketing Director suggests using the RFM (Recency, Frequency, Monetary) model and Marketing department requests the Data Analytics department to build an automated RFM analysis pipeline using Python. This will enable scalable, accurate customer segmentation to support personalized marketing efforts.

-> *Analyze the current situation of the company and give suggestions to the Marketing team*

-> *Suggestions to the Marketing and Sales teams with the retail model of the Superstore company, which of the 3 indicators R, F, M should be most concerned about?*

# **EDA**

##**Initial look**
"""

#size
ecommerce_retail.shape

#info
ecommerce_retail.info()

#10firstline
ecommerce_retail.head(10)

#descriptive statistics
ecommerce_retail.describe()

"""##**Inspection & Validation**"""

#Overview 1 initial
profile = ProfileReport(ecommerce_retail, title="EDA Report", explorative=True)
profile.to_notebook_iframe()

"""###Data type
1. Change the dtype of InvoiceID & StockCode & CustomerID to STRING because InvoiceID usually includes numbers + letters
2. Description, Country -> description / country name -> change the dtype of these 2 columns to STRING


"""

#dtype
ecommerce_retail.dtypes

# change dtype
ecommerce_retail['InvoiceNo'] = ecommerce_retail['InvoiceNo'].astype('string')
ecommerce_retail['StockCode'] = ecommerce_retail['StockCode'].astype('string')
ecommerce_retail['Description'] = ecommerce_retail['Description'].astype('string')
ecommerce_retail['CustomerID'] = ecommerce_retail['CustomerID'].astype('string')
ecommerce_retail['Country'] = ecommerce_retail['Country'].astype('string')

#check again dtype
ecommerce_retail.dtypes

"""###Missing Value
Description, CustomerID
-> Next step:
1. Remove rows without Description information because Unit Price = 0 and no Customer ID information
2. Remove rows without CustomerID information because it will not be possible to identify the customer segment
"""

#Statistics of columns with Missing Value
ecommerce_retail.isnull().sum()

#check why CustomerID is null so much

print(ecommerce_retail[ecommerce_retail.CustomerID.isnull()].head())

print('')

print(ecommerce_retail[ecommerce_retail.CustomerID.isnull()].tail())

ecommerce_retail['Day'] =  pd.to_datetime(ecommerce_retail['InvoiceDate']).dt.date
ecommerce_retail['Month'] = ecommerce_retail['Day'].apply(lambda x: str(x)[:-3])

df_group_day = ecommerce_retail[ecommerce_retail.CustomerID.isnull()][['Month','InvoiceNo']].groupby(['Month']).count().reset_index().sort_values(by = ['Month'], ascending = True)
df_group_day.head(50)

#Remove rows without Description
ecommerce_retail = ecommerce_retail[ecommerce_retail['Description'].notna()]

#Remove rows without CustomerID
ecommerce_retail = ecommerce_retail[ecommerce_retail['CustomerID'].notna()]

#check
ecommerce_retail.isnull().sum()

"""###Unique Value"""

ecommerce_retail.nunique()

ecommerce_retail["InvoiceNo"].value_counts()

ecommerce_retail["StockCode"].value_counts()

ecommerce_retail["CustomerID"].value_counts()

ecommerce_retail["Country"].value_counts()

"""###Duplicate Value
Duplicates: 5225 rows -> Next step: Delete rows
"""

ecommerce_retail.duplicated().sum()

ecommerce_retail = ecommerce_retail.drop_duplicates()

#Check lại
ecommerce_retail.duplicated().sum()

"""###Outliers
Next step: no action because some customers buy small quantities, some customers buy large quantities
"""

Q1 = ecommerce_retail['Quantity'].quantile(0.25)
Q3 = ecommerce_retail['Quantity'].quantile(0.75)
IQR = Q3 - Q1

lower_bound = Q1 - 1.5 * IQR
upper_bound = Q3 + 1.5 * IQR

ecom_outliers = ecommerce_retail[(ecommerce_retail['Quantity'] < lower_bound) | (ecommerce_retail['Quantity'] > upper_bound)]
ecom_outliers

"""###Valid Value
- Rows with Quantity < 0 -> remove because this is a return
- Rows with Unit Price < 0 -> remove

####Detect & Handle - Quantity Value < 0
"""

#check reason data Quantity < 0
print('Print some values ​​with Quantity < 0')
print(ecommerce_retail[ecommerce_retail.Quantity < 0].head())
print('')

#check the reason the Quantity column < 0 is because the transaction was canceled or not?
print('Check the reason the Quantity column < 0 is because the transaction was canceled or not?')
ecommerce_retail['InvoiceNo'] = ecommerce_retail['InvoiceNo'].astype(str)
ecommerce_retail['check_cancel'] = ecommerce_retail['InvoiceNo'].apply(lambda x: True if x[0] == 'C' else False)
print(ecommerce_retail[(ecommerce_retail.Quantity < 0) & (ecommerce_retail.check_cancel == True)].head())

print('')
ecommerce_retail[(ecommerce_retail.Quantity < 0) & (ecommerce_retail.check_cancel == False)].head()

#drop data with Quantity < 0
ecommerce_retail = ecommerce_retail[ecommerce_retail['Quantity'] > 0]

#drop data has order cancelled
ecommerce_retail = ecommerce_retail[ecommerce_retail.check_cancel == False]
ecommerce_retail = ecommerce_retail.replace('nan', None)
ecommerce_retail = ecommerce_retail.replace('Nan',None)

"""####Detect & Handle - Unit Price Value < 0"""

#check Unit Price < 0
print('Print some values ​​with UnitPrice < 0')
ecommerce_retail[ecommerce_retail.UnitPrice < 0].head()

#drop data có Unit Price < 0
ecommerce_retail = ecommerce_retail[ecommerce_retail['UnitPrice'] > 0]

"""###Distribution"""

df_pos_qty = ecommerce_retail[ecommerce_retail['Quantity'] > 0]
plt.hist(np.log1p(df_pos_qty['Quantity']), bins=50)
plt.title("Log Distribution of Quantity")
plt.show()

# Tạo biến TotalPrice
ecommerce_retail['TotalPrice'] = ecommerce_retail['Quantity'] * ecommerce_retail['UnitPrice']

# Giữ lại các dòng có TotalPrice > 0 để tránh lỗi log
df_positive_total = ecommerce_retail[ecommerce_retail['TotalPrice'] > 0]

# Vẽ histogram của log(1 + TotalPrice)
plt.figure(figsize=(7, 4))
plt.hist(np.log1p(df_positive_total['TotalPrice']), bins=50, color='lightgreen', edgecolor='black')

plt.title('Log-Scaled Distribution of Total Transaction Value')
plt.xlabel('log(1 + TotalPrice)')
plt.ylabel('Frequency')
plt.grid(True)
plt.show()

#Overview last time
profile = ProfileReport(ecommerce_retail, title="EDA Report", explorative=True)
profile.to_notebook_iframe()

"""#**Data Processing**

###Prepare
"""

#Add TotalPrice Column
ecommerce_retail['TotalPrice'] = ecommerce_retail['Quantity'] * ecommerce_retail['UnitPrice']

#assign reference date
import datetime as dt
ref_date = dt.datetime(2011, 12, 31)

"""###Calculation R,F,M mark"""

rfm = ecommerce_retail.groupby('CustomerID').agg({
    'InvoiceDate': lambda x: (ref_date - x.max()).days,   # Recency
    'InvoiceNo': 'nunique',                               # Frequency
    'TotalPrice': 'sum'                                   # Monetary
}).reset_index()

rfm.columns = ['CustomerID', 'Recency', 'Frequency', 'Monetary']

"""###Calculate R, F, M scores with qcut() & RFM score"""

# Recency: low score -> new customer (the newer the better)
rfm['R_score'] = pd.qcut(rfm['Recency'], 5, labels=[5, 4, 3, 2, 1])

# Frequency & Monetary: high score is good customer
f_bins = pd.qcut(rfm['Frequency'], q=5, duplicates='drop')
rfm['F_score'] = f_bins.cat.codes + 1  # encode labels as 1, 2, ...

m_bins = pd.qcut(rfm['Monetary'], q=5, duplicates='drop')
rfm['M_score'] = m_bins.cat.codes + 1

rfm['RFM Score'] = rfm['R_score'].astype(str) + rfm['F_score'].astype(str) + rfm['M_score'].astype(str)
rfm.head()

"""###Customer segmentation by RFM score"""

#Split RFM Score string into list, then explode each line
segmentation['RFM Score'] = segmentation['RFM Score'].str.split(',')  # Split string into list
segmentation = segmentation.explode('RFM Score').reset_index(drop=True)  # Convert each RFM Score to a row

segmentation

rfm

# Rename columns to avoid errors
rfm.rename(columns={'RFM Score': 'RFM_Score'}, inplace=True)
segmentation.rename(columns={'RFM Score': 'RFM_Score'}, inplace=True)

# Make sure RFM_Score columns are all integers
rfm['RFM_Score'] = rfm['RFM_Score'].astype(int)
segmentation['RFM_Score'] = segmentation['RFM_Score'].astype(int)

# Merge segmentation with rfm table by column 'RFM_Score'
rfm_segmented = rfm.merge(segmentation, on='RFM_Score', how='left')

rfm_segmented

rfm_segmented['Segment'].value_counts()

"""###Customer segmentation by characteristics from RFM segment"""

def map_to_group(segment):
    if segment in ['Champions', 'Loyal']:
        return 'Loyal Core'
    elif segment in ['Need Attention','At Risk', 'Cannot Lose Them']:
        return 'Save-Worthy'
    elif segment in ['Potential Loyalist', 'Promising', 'New Customers']:
        return 'Growth Potential'
    elif segment in ['Hibernating customers', 'About To Sleep']:
        return 'Inactive'
    elif segment in ['Lost customers']:
        return 'Lost'
    else:
        return 'Other'  # optional: for unexpected values

# Apply to lambda
rfm_segmented['Customer_Group'] = rfm_segmented['Segment'].apply(lambda x: map_to_group(x))

rfm_segmented.head(20)

"""#**Data Visualization & Analysis**

###Recency, Frequency, Monetary Distribution
→ Understand the overview of customer behavior in each dimension: recent, frequent, spending

####Distribution (remove outliers)
"""

fig, axs = plt.subplots(1, 3, figsize=(20, 5))

# Recency
sns.histplot(data=rfm_segmented, x='Recency', bins=30, kde=True, ax=axs[0], color='skyblue')
axs[0].set_title('Recency Distribution')

# Frequency (filter <= 50 to remove outliers -- Some customers buy hundreds of times, causing the distribution to be skewed, making it difficult to observe the majority)
sns.histplot(data=rfm_segmented[rfm_segmented['Frequency'] <= 50],
             x='Frequency', bins=30, kde=True, ax=axs[1], color='salmon')
axs[1].set_title('Frequency Distribution (<=50)')

# Monetary (filter <= 10000 to see the main focus clearly -- There are some customers with extremely large spending causing distribution distortion - need to separate for separate analysis)
sns.histplot(data=rfm_segmented[rfm_segmented['Monetary'] <= 10000],
             x='Monetary', bins=30, kde=True, ax=axs[2], color='seagreen')
axs[2].set_title('Monetary Distribution (<=10k)')

plt.tight_layout()
plt.show()

"""####Distribution (Outliers for high spenders)"""

monetary_outliers = rfm_segmented[rfm_segmented['Monetary'] > 10000]
monetary_outliers.shape  #See how many customers

monetary_outliers.describe()

sns.histplot(data=monetary_outliers, x='Monetary', bins=30, kde=True, color='purple')
plt.title("Distribution of High Monetary Outliers (>10,000)")
plt.show()

# Compare outlier vs total RFM average
compare_df = pd.DataFrame({
    'All_Customers': rfm_segmented[['Recency', 'Frequency', 'Monetary']].mean(),
    'Outliers_Only': monetary_outliers[['Recency', 'Frequency', 'Monetary']].mean()
}).round(1)

compare_df

monetary_outliers['Segment'].value_counts()

"""####***Assessment (step 1)***
1. **Recency Distribution**
- Strong right-skewed distribution: Many customers have low Recency (ie, recently purchased), concentrated in the last 30–60 days.
- A small number of customers have very high Recency (200–400 days): These are customers who have not returned for a long time, with a high risk of leaving.

→ *Insight:*
+ Most customers still interact relatively recently, this is a positive signal.
+ Need to consider campaigns to retain customers with Recency > 150 (low repurchase)

2. **Frequency Distribution**
- Filtered customers with Frequency > 50 to focus on the large group.
- Very clear right-skewed distribution: Most customers only buy 1–3 times, very few people buy >10 times.

→ *Insight:*
+ The customer group is mainly trial or one-time buyers.
+ Potential to increase Frequency with loyalty, up-sell, reminder programs.

3. **Monetary Distribution**
- Filter customers with Monetary > 10,000 to see the majority.
- Obvious right deviation: Most customers spend less than 2000 units (many in the range of 0–1000).
- There are some very large spending outliers (the cut part), need to analyze separately (*)

→ *Insight:*
+ Low-value customers make up the majority -> easy to scale but also easy to leave.
+ The high-spending group (filtered out) can be VIP / Big Spender, need a separate strategy to retain.

4. **Customer group with large spending (>10000)**
- The outlier group buys more frequently (30.6 vs. 4.3), more recently (39.5 vs. 113) and spends ~17 times higher than the overall average
- This customer group is mainly Champions, with absolute dominance: 85/104 customers (≈ 82%), the remaining groups only account for a very small proportion.

*→ Insight:*
- The group of customers with outstanding spending has very positive behavior:
Buy a lot, buy regularly, return recently → very loyal and have high value.
- Most are in the "Champions" segment:
This is an extremely important group, which needs to be identified and taken care of specially (exclusive offers, priority support, retention campaigns...).
- Strong impact on overall analysis results:
If not separated, the outlier group can skew the overall average and obscure the trend of the majority of remaining customers.

**CONCLUSION**

*SuperStore's status*
- Quite active customer group (Good Recency)
- Low repeat purchase rate, most of them only buy 1-2 times → need to stimulate F increase
- The large-spending customer group has great potential, should be separated to take care of and exploit long-term value

*Suggestion*
- Retargeting the group with high Recency but low Frequency to promote repurchase
- Build a separate "VIP/Elite" program for the large-spending group to retain and upsell effectively
- Segment customers to personalize marketing campaigns from the next step

###Customer Segmentation

→ Identify which groups are dominating the data.

####Total number of customers & revenue by segment
"""

# Aggregate by Segment
segment_summary = rfm_segmented.groupby('Segment').agg({
    'CustomerID': 'count',
    'Monetary': 'sum'
}).rename(columns={'CustomerID': 'Num_Customers', 'Monetary': 'Total_Revenue'})

# Calculate additional percentage
segment_summary['%_Customers'] = (segment_summary['Num_Customers'] / segment_summary['Num_Customers'].sum() * 100).round(2)
segment_summary['%_Revenue'] = (segment_summary['Total_Revenue'] / segment_summary['Total_Revenue'].sum() * 100).round(2)

# Sort by revenue
segment_summary.sort_values(by='Total_Revenue', ascending=False)

"""####Customer segment structure"""

#Number of customers by segment
plt.figure(figsize=(9,5))
sns.countplot(data=rfm_segmented, x='Segment', order=rfm_segmented['Segment'].value_counts().index)
plt.xticks(rotation=45)
plt.title('Số lượng khách hàng theo từng phân khúc (Segment)')
plt.xlabel('Segment')
plt.ylabel('Số lượng khách hàng')
plt.tight_layout()
plt.show()

#Total Revenue by Segment
monetary_by_segment = rfm_segmented.groupby('Segment')['Monetary'].sum().sort_values(ascending=False)

# Bar chart
plt.figure(figsize=(9,5))
sns.barplot(x=monetary_by_segment.index, y=monetary_by_segment.values)
plt.xticks(rotation=45)
plt.ylabel('Tổng chi tiêu (Monetary)')
plt.title('Tổng chi tiêu theo từng phân khúc khách hàng')
plt.tight_layout()
plt.show()

"""####***Assessment (step 2)***
**1. Core group (Champions & Loyal)**
- Champions account for about 12.31% of customers but generate up to 54.88% of revenue, which is a strategic customer group that needs to be prioritized to maintain and develop
- Loyal accounts for 5.44% but contributes 9.96% of revenue, showing the potential to convert into Champions if properly cared for.

→ *Risk*: Losing the Champions group will cause a sharp decrease in revenue, and if Loyal cannot be upgraded, the source of loyal customers will be narrowed

→ *Recommendation*:
- Focus on gratitude, VIP incentives, building a loyal community for Champions
- Strengthen the program to encourage referrals, give upgrade rewards to the Loyal group to develop them into Champions

**2. Potential Group (Promising, Potential Loyalist, New Customers)**

This group accounts for a large proportion of new customers but currently has low revenue (New Customers account for 11.75% of customers but only contribute 1.35% of revenue). This is a customer group that needs to be nurtured properly to convert into loyal customers.

→ *Opportunity*: With an effective onboarding process, preferential policies and personalized care, this group can develop into Loyal or even Champions in the future

→ *Recommendation*: Build a new customer care system through periodic emails, product instructions, offer repurchase incentives, and create personalized customer experiences to increase retention.

**3. Groups with signs of leaving (Need Attention, At Risk, About To Sleep, Hibernating)**

This group is losing engagement and is at high risk of leaving, but still contributes significantly to revenue (e.g. At Risk group accounts for 5.53% of customers but contributes 6.46% of revenue)

→ *Risk*: Failure to retain valuable customers in a timely manner will result in losing valuable customers, affecting revenue stability

→ *Recommendation*: Apply personalized reactivation campaigns, limited-time offers, and reiterate the reasons why customers chose the product to stimulate repurchase and maintain engagement.

**4. High-risk group (Cannot Lose Them)**

Although accounting for only 5.25% of customers, this group contributes 3.99% of revenue but is showing signs of losing VIP customers

→ *Risk*: Losing this VIP group causes great losses in revenue and brand reputation

→ *Recommendation*: Provide special care by contacting directly, surveying the reasons for reduced purchases, giving exclusive vouchers, creating personalized incentives to retain customers

**5. Lost Customers**
Accounts for the largest proportion (14.29%) but contributes very little revenue (1.61%)

→ *Risk*: Continuing to invest in mass marketing on this group can easily waste resources and cause low ROI

→ *Recommendation*: Optimize the budget by reducing advertising spending on this group, only apply selective remarketing through A/B test programs, or remove from the marketing list if ineffective

**Summary**: SuperStore is heavily dependent on the small Champions group that generates the main revenue, and needs to maintain and develop the Loyal group to ensure a stable source of loyal customers. At the same time, it is necessary to focus on nurturing new potential customers and reactivating groups that show signs of leaving to maintain sustainable growth. At the same time, it is necessary to avoid wasting resources on the lost group.

###Group Value Analysis
→ Understand each customer segment based on the value it brings

####Summarize group values ​​by Segment
"""

segment_value = rfm_segmented.groupby('Segment').agg(
    Num_Customers=('CustomerID', 'count'),
    Total_Revenue=('Monetary', 'sum'),
    Avg_Revenue=('Monetary', 'mean'),
    Avg_Frequency=('Frequency', 'mean'),
    Avg_Recency=('Recency', 'mean')
).round(2).sort_values(by='Total_Revenue', ascending=False)

segment_value

"""####Compare group values"""

#Bar chart comparing Avg_Revenue by segment
plt.figure(figsize=(9, 5))
sns.barplot(data=segment_value.reset_index(),
            x='Segment', y='Avg_Revenue')
plt.title('Doanh thu trung bình mỗi khách hàng theo phân khúc')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#Avg_Recency
plt.figure(figsize=(9, 5))
sns.barplot(data=segment_value.reset_index(),
            x='Segment', y='Avg_Recency')
plt.title('Recency trung bình mỗi phân khúc khách hàng')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

#Avg_Frequency
plt.figure(figsize=(9, 5))
sns.barplot(data=segment_value.reset_index(),
            x='Segment', y='Avg_Frequency')
plt.title('Tần suất mua trung bình mỗi khách hàng (Avg Frequency)')
plt.xticks(rotation=45)
plt.tight_layout()
plt.show()

"""####***Assessment step 3***
**1. Core customer group (Champions & Loyal)**

- Champions: 534 customers (~12%), revenue of 4.8 million (>50%), average spending of 9,134/person, purchase frequency of 15.86 times.

- Loyal: 5.44% of customers, average spending of 3,749/person, purchase frequency of 7.37 times.

-> **Insight:** This is the group that generates the largest revenue, has high brand loyalty

-> **Risk:** Over-reliance on this group can cause revenue to fluctuate sharply if they reduce interaction or leave

->**Recommendation:** Prioritize gratitude programs, VIP incentives, reward points, separate customer care and allow early access to new products to increase engagement and long-term retention

**2. High-value customer groups but at risk of leaving (At Risk & Cannot Lose Them)**

- At Risk: 5.53% of customers, spend 2,391/person, purchase frequency 4.96 times.

- Cannot Lose Them: 5.25% of customers, revenue accounts for 3.99%, high Recency (235 days).

-> **Insight:** Revenue from this group is still high but there are signs of decreased interaction, risk of losing high-value customers

-> **Risk:** Losing this group causes significant loss of revenue and affects brand reputation

-> **Recommendation:** Implement personalized offers, exclusive vouchers, thank-you messages, build special engagement activities to stimulate interaction and retain customers

**3. Potential customer group (Potential Loyalist, Promising & New Customers)**
- Total number of Potential Loyalist, Promising customers is over 700, New Customers is 510 KH
- Average spending of Promising group is 1437.1/person, Potential List is 699.00/person, New Customers is 235.8/person
- Recency is still good but frequency is low.

-> **Insight:** New and potential customers need to be nurtured to develop into loyal customers

-> **Opportunity:** Increase long-term revenue by nurturing and converting this group into loyal customers

-> **Recommendation:** Build a systematic onboarding process, personalize email marketing, repurchase incentives, encourage referrals and upsell related products

**4. Hibernating & About To Sleep customers**

- Need Attention: Average spending is quite stable: 1734.93/person, showing signs of decreasing interaction (Recency is 45.59 days) and decreasing purchase frequency (Frequency is 4.64 times)
- Hibernating: 491 customers, low average spending (346.20/person), high Recency, low Frequency
- About To Sleep: 328 customers, average spending is quite low (492.76/person), also showing a tendency to decrease activity, high Recency, low Frequency

-> **Insight:** The group is at risk of being lost if not reactivated soon.

-> **Risk:** Losing this group will affect long-term revenue

-> **Recommendation:** Apply flash sales, abandoned cart reminders, personalized demand surveys to reactivate and attract customers back

**5. Lost Customers**
- 620 customers, highest Recency (296 days), low spending 0.14 million, very low average spending: 231.26/person.

-> **Insight:** Almost no value for current revenue.

-> **Risk:** Continuing to invest in mass can easily waste budget.

-> **Recommendation:** Reduce mass budget, selective remarketing with A/B testing, remove from file if ROI is negative.

###Relationship between indicators
→ Identify customer consumption behavior characteristics in each dimension.

1. R&F -> Do customers buy a lot and recently?
2. R&M -> Do customers spend a lot but have not returned for a long time?
3. F&M -> Do customers who buy a lot spend a lot of money? (avoid small customers who buy a lot but have low value)
4. Understand the relationship between the indicators Recency (R), Frequency (F), Monetary (M).

Detect potential or unusual customer groups.
From there, clearly identify the characteristics of each group, and suggest appropriate strategies.
"""

#Correlation
rfm_corr = rfm_segmented[['Recency', 'Frequency', 'Monetary']].corr()

plt.figure(figsize=(5, 4))
sns.heatmap(rfm_corr, annot=True, cmap='coolwarm', fmt='.2f')
plt.title('Correlation Matrix giữa Recency, Frequency, Monetary')
plt.show()

# Cast to string to handle explicit classification in heatmap
rfm_segmented['R_score'] = rfm_segmented['R_score'].astype(str)
rfm_segmented['F_score'] = rfm_segmented['F_score'].astype(str)
rfm_segmented['M_score'] = rfm_segmented['M_score'].astype(str)

plt.figure(figsize=(18, 5))

# Heatmap 1: R vs F
plt.subplot(1, 3, 1)
rf_matrix = rfm_segmented.groupby(['R_score', 'F_score'])['CustomerID'].count().unstack().fillna(0)
rf_matrix = rf_matrix.astype(float)
sns.heatmap(rf_matrix, annot=True, fmt='g', cmap='YlGnBu')
plt.title('R_score vs F_score')
plt.xlabel('F_score')
plt.ylabel('R_score')

# Heatmap 2: R vs M
plt.subplot(1, 3, 2)
rm_matrix = rfm_segmented.groupby(['R_score', 'M_score'])['CustomerID'].count().unstack().fillna(0)
rm_matrix = rm_matrix.astype(float)
sns.heatmap(rm_matrix, annot=True, fmt='g', cmap='Oranges')
plt.title('R_score vs M_score')
plt.xlabel('M_score')
plt.ylabel('R_score')

# Heatmap 3: F vs M
plt.subplot(1, 3, 3)
fm_matrix = rfm_segmented.groupby(['F_score', 'M_score'])['CustomerID'].count().unstack().fillna(0)
fm_matrix = fm_matrix.astype(float)
sns.heatmap(fm_matrix, annot=True, fmt='g', cmap='PuBuGn')
plt.title('F_score vs M_score')
plt.xlabel('M_score')
plt.ylabel('F_score')

plt.tight_layout()
plt.show()

"""####***Assessment step 4***

**1. The high-end customer group is forming (R=5, F=3–4, M=4–5)**

- ~565 customers with high Recency (recent purchases), Frequency ≥ 3, Monetary ≥ 4 → loyal & high-spending customer files
- This is a **new core customer** with great potential to develop into Champions.

-> *Opportunity:* Can become the main revenue-generating group in the future if well nurtured

-> *Recommendation:* Create early VIP incentives, separate customer service, experience the product first, and a tiered point accumulation program.

**2. Customers who have spent a lot but are at risk of leaving (R=1, M=4–5)**

- Group of customers with large order values ​​but have not returned for a long time
- Lowest Recency, very high spending (Monetary = 4–5)

-> *Risk:* Losing this group means losing a large source of revenue.

-> *Recommendation:* Send reactivation emails, give “welcome back” vouchers, exclusive offers (personalized flash sales)

**3. Customers who buy many times but low order values ​​(F=4, M=1–2)**

- High frequency (4 times), but spending value is only at a low level → “often buy but not spend a lot” group

- This is a **small, loyal group**, whose potential has not been fully exploited.

-> *Opportunity:* Can increase ARPU by upselling.

-> *Recommendation:* Suggest product combos, discounts according to spending levels, upgrade payment experience (free shipping if reaching the threshold).

**4. Customers who have just returned but are not of high value (R=5, F=1, M=1)**

- Recently purchased (R=5) but still buy little & small → potential customers convert

-> *Opportunity:* Turn into loyal customers if taken care of at the right time

-> *Recommendation:* Implement "second purchase" offers, better product experience onboarding, gentle upsell.

#**Conclusion -> Insights & Recommendations**

### Conclusion on the status of SuperStore & Suggestions for Marketing team

#####**Status of SuperStore**
(1) Heavily dependent on loyal customer group (Champions)
- Only accounts for ~12% of customers but generates >50% of revenue.
- If this group is not maintained, revenue will likely decline seriously

(2) Low repeat purchase rate, one-time customers are still very numerous
- Most customers only buy 1-2 times, spend small amounts (F=1, M=1 still account for the majority) so campaigns to increase Frequency and ARPU (Average Revenue per user) are needed

(3) There is a VIP group that used to spend a lot but is leaving
- Group R=1, M=4–5 has high order value but has not returned for a long time.

→ Risk of losing a large source of revenue if there is no early reactivation campaign.

(4) Potential customer files have not been converted effectively
- Promising, Potential Loyalist, New Customer: Good Recency but Low Frequency and Spending → Opportunity for nurturing.

(5) There are many customers who are “hibernating” or have lost value
Hibernating, About To Sleep Lost Customers account for > 30% of customers but contribute low revenue -> Should not mass market to this group if there is no positive ROI index

#####**Suggestions for Marketing Team**
(1) Current customer care strategy (Retention)
- Prioritize Champions & Loyal group: VIP offers, reward points, priority support, early-access products
- At Risk & Cannot Lose Them group: Re-engagement campaigns, survey reasons for leaving, personalized offers

(2) Nurturing strategy (Nurturing)
- Promising, Potential Loyalist, New Customer: Remarketing script, repeat purchase offers, email onboarding, personalized messages

(3) Reactivation strategy (Reactivation)
- Hibernating, About to Sleep, Need Attention: Limited flash sale, emotional messages ("Do you miss this product?"), exclusive offers.

(4) Resource optimization strategy
- Lost Customers: Stop mass marketing, only try comeback A/B testing → if ROI is low, remove from the file.

###Suggestions for Marketing and Sales teams with the retail model of Superstore company, which of the 3 indexes R, F, M should be most concerned with?
-> each team should prioritize each RFM index

#####**Team Marketing**
-> Prioritize **Recency (R)** because:

(1) Core goals of Team Marketing
- Retain customers (retention)
- Increase conversion rate from advertising/email/SMS campaigns.
- Optimize marketing costs/efficiencies (CPL, ROAS, CTR, open rate).
- Nurture the group of customers who have not returned (winback/lapsed segment).
-> All of the above goals depend heavily on knowing whether customers are still "hot" or "cold" → That is Recency

(2) Why is Recency the most important indicator?
- Recency reflects the "hotness" of customers: If customers have just purchased → still remember the brand → easy to click on ads, easy to interact → higher remarketing efficiency (This is the group with the highest conversion rate if doing remarketing)
- Not considering Recency → easy to "burn money" on customers who have "fallen away"
  + High F, high R (buy regularly but for a long time) -> May have left the brand. Sending promotions to this group is easy to waste budget)
  + High M, high R -> Customers used to spend a lot, but now are no longer interested. Low response rate despite attractive promotions
- Recency helps Marketing classify strategic groups - the foundation for Lifecycle Marketing
  + Active (Recently purchased) -> Maintain interaction rhythm → upsell
  + Warm (Recently purchased but not necessarily loyal) -> Nurture → promote repurchase
  + Cool (Paused but still have the ability to return) -> Reactivate → light retargeting
  + Cold (Stopped purchasing for quite a while) -> Revive → winback campaign
  + Lost (Risk of losing completely) -> Classify to reduce marketing costs or eliminate

Thus, Recency helps the Marketing team send to the right people, at the right time, thereby increasing conversion rates, optimizing budgets, and building automation scenarios suitable for each stage in the customer journey.

#####**Team Sales**
→ Frequency (F) should be prioritized because:

(1) Core goals of the Sales Team:
- Maximize sales per customer and per reporting period (week/month/quarter)
- Increase closing rate and upsell for existing customers
- Build long-term relationships with high-value customers
- Prioritize resources (consultants, time) to the most potential group

(2) Why is Frequency the most important indicator for Sales?
- Frequency shows the actual level of engagement between customers and the brand
  + Customers with high F are customers who come back to buy many times, meaning they have been "served" many times, find it trustworthy, convenient, and meet their needs.
→ This is an "asset" of the Sales team because customers are familiar with the brand → easy to approach, easy to chat, easy to suggest the next product.
- F helps Sales identify “real potential” customer groups
→ Not only spend a lot (M) but buy regularly → prioritize nurturing to create sustainable revenue.
- The higher the F → The lower the sales cost → The higher the profit margin
  + With customers who have bought many times, the Sales team does not need to spend time introducing again, does not need to deal with too many psychological barriers → close orders faster, lower Sales costs.
→ This is an “easy win” group that helps achieve targets quickly and sustainably
- F opens up opportunities for Up-sell / Cross-sell strategies
→ Customers have the habit of buying repeatedly → easy to sell premium packages, combos, additional services.
- F helps to group & personalize care: Sales can divide customers by purchase frequency (High-F: take care → close big orders; Medium-F: suggest increasing purchase frequency → combo; Low-F: re-evaluate the cause → remove barriers (price, convenience, advice...))

In short, Frequency helps the Sales Team identify the right potential customers, increase the closing rate, optimize costs and build sustainable revenue.
"""