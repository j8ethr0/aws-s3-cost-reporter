import boto3
import json
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
import argparse

# AWS setup
session = boto3.Session(region_name="eu-west-1")
cost_client = session.client('ce')
ses_client = session.client('ses')

# Email settings
SENDER_EMAIL = "admin@example.com"
RECIPIENT_EMAIL = "awscostreport@example.com"
SUBJECT = "S3 Cost Breakdown"
CHARSET = "UTF-8"

# HTML Template
HTML_TEMPLATE = """
<html>
<head>
<style>
	body {{
		font-family: 'Roboto', 'Arial', sans-serif;
		background: linear-gradient(135deg, #1e222a, #2c3e50);
		color: #e0e0e0;
		margin: 0;
		padding: 10px;
		display: flex;
		flex-direction: column;
		align-items: center;
		min-height: 100vh;
	}}
	h2 {{
		color: #58a6ff;
		text-align: center;
		text-transform: uppercase;
		letter-spacing: 1px;
	}}
	table {{
		width: 70%;
		border-collapse: collapse;
		margin: 0 auto;
		text-align: center;
		margin-bottom: 20px;
		border-radius: 8px;
		overflow: hidden;
		box-shadow: 0 6px 12px rgba(0, 0, 0, 0.3);
		background: linear-gradient(135deg, #161b22, #21262d);
		border: 1px solid #30363d;
	}}
	th, td {{
		padding: 12px 16px;
		text-align: left;
		border-bottom: 1px solid #383c44;
		white-space: nowrap;
		overflow: hidden;
		text-overflow: ellipsis;
	}}
	th {{
		background: linear-gradient(135deg, #383c44, #4a4f5b);
		color: #f0f0f0;
		font-weight: 600;
		font-size: 16px;
		border-bottom: 2px solid #5aa7ff;
	}}
	tr:nth-child(even) {{ background-color: #2a2e36; }}
	tr:hover {{ background-color: rgba(255, 255, 255, 0.1); transition: 0.3s ease-in-out; }}

	/* 🎨 Highlighting */
	.high-cost {{ background-color: #FFA500; color: white; font-weight: bold; }}  /* 🔴 Deep Red */
	.medium-cost {{ background-color: #ffcc00; color: black; font-weight: bold; }}  /* 🟡 Bright Gold */
	.low-cost {{ color: #4caf50; }}  /* Green */
	.bucket-name {{ color: #64b5f6; font-weight: 600; }}  /* Blue */
	.cost-purple {{ color: #dd69f1; font-weight: 600; }}  /* Purple */
</style>
</head>
<body>
	<h2>{title} - {month_year}</h2>
	<table>
		<tr><th>Bucket Name</th><th>Total Cost (USD)</th></tr>
		{rows}
	</table>
</body>
</html>
"""

def get_s3_costs(year, month):
	start_date = f"{year}-{month:02d}-01"
	end_date = f"{year}-{month:02d}-{datetime(year, month, 1).replace(day=28).day}"
	response = cost_client.get_cost_and_usage(
		TimePeriod={'Start': start_date, 'End': end_date},
		Granularity='MONTHLY',
		Metrics=['UnblendedCost'],
		GroupBy=[{'Type': 'DIMENSION', 'Key': 'SERVICE'}, {'Type': 'TAG', 'Key': 'BucketName'}]
	)
	bucket_costs = {}
	for result in response['ResultsByTime'][0]['Groups']:
		service = result['Keys'][0]
		if 'Amazon Simple Storage Service' in service:
			bucket = result['Keys'][1] if len(result['Keys']) > 1 and result['Keys'][1] != "None" else "Unknown"
			bucket = bucket.replace("BucketName$", "").strip()  # Fix bucket name formatting
			cost = float(result['Metrics']['UnblendedCost']['Amount'])
			bucket_costs[bucket] = bucket_costs.get(bucket, 0) + cost
	return dict(sorted(bucket_costs.items(), key=lambda item: item[1], reverse=True))

def send_email(report_html, month_year):
	msg = MIMEMultipart()
	msg['From'] = SENDER_EMAIL
	msg['To'] = RECIPIENT_EMAIL
	msg['Subject'] = SUBJECT
	msg.attach(MIMEText(report_html, 'html'))
	ses_client.send_raw_email(Source=SENDER_EMAIL, Destinations=[RECIPIENT_EMAIL], RawMessage={'Data': msg.as_string()})

def generate_report(year, month):
	bucket_costs = get_s3_costs(year, month)
	rows = ""
	for bucket, cost in bucket_costs.items():
		css_class = ""
		if cost > 200:
			css_class = "high-cost"
		elif cost > 100:
			css_class = "medium-cost"
		elif cost > 50:
			css_class = "low-cost"

		rows += f"<tr class='{css_class}'>" \
				f"<td class='bucket-name'>{bucket}</td>" \
				f"<td class='cost-purple'>${cost:.2f}</td>" \
				f"</tr>"

	month_year_str = datetime(year, month, 1).strftime("%B %Y")  # Converts "2025-03" to "March 2025"
	report_html = HTML_TEMPLATE.format(title="S3 Cost Breakdown", month_year=month_year_str, rows=rows)
	send_email(report_html, month_year_str)

if __name__ == "__main__":
	parser = argparse.ArgumentParser()
	parser.add_argument("year", type=int, help="Year (e.g., 2025)")
	parser.add_argument("month", type=int, help="Month (1-12)")
	args = parser.parse_args()
	generate_report(args.year, args.month)