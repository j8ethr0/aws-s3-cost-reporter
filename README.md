# aws-s3-cost-reporter
This Python script retrieves and emails a monthly (to date) cost breakdown for your AWS S3 buckets. It uses the AWS Cost Explorer API to fetch the data and sends a formatted HTML email report via AWS SES.

# AWS S3 Cost Reporter

## Features

*   **Monthly Cost Breakdown:**  Provides a clear table of S3 bucket costs for a specified month.
*   **HTML Email Report:**  Sends a well-formatted HTML email with cost highlighting.
*   **Cost Highlighting:** Uses color-coding to highlight buckets with high, medium, and low costs.
*   **AWS SES Integration:**  Sends emails using the AWS Simple Email Service (SES).
*   **Command-Line Arguments:**  Takes the year and month as command-line arguments.
*    **Formatted output:** Uses HTML template to beautify the output.

## Prerequisites

Before running the script, ensure you have the following:

1.  **AWS Account:**  An active AWS account with access to Cost Explorer and SES.
2.  **AWS Credentials:**  Configure your AWS credentials.  The easiest way is to use the AWS CLI and run `aws configure`.  This script uses the `boto3` library, which automatically picks up credentials from the standard locations (environment variables, AWS config file).
3.  **Python 3:**  The script is written in Python 3.  Make sure you have Python 3.6 or later installed.
4.  **Boto3 Library:** Install the `boto3` library:
	```bash
	pip install boto3
	```
5.  **SES Setup:**
	*   **Verified Email Address:** You must have a verified email address or domain in AWS SES to send emails.  In this script, `sender` needs to be verified.
	*   **SES in Production (Optional):**  If your SES account is still in the sandbox, you can only send emails to verified recipient addresses.  To send to any recipient, you'll need to request production access from AWS.

## Script Setup

1.  **Clone the Repository:**
	```bash
	git clone <your-repository-url>
	cd <repository-directory>
	```

2.  **Configuration:**
	*   **AWS Region:** Update the `region_name` in the `boto3.Session()` call if your resources are not in `eu-west-1`.
	*   **Email Addresses:** Modify `SENDER_EMAIL` and `RECIPIENT_EMAIL` to your desired sender and recipient email addresses.  Make sure the sender email is verified in SES.
	*   **Cost Thresholds (Optional):** Adjust the cost thresholds (200, 100, 50) in the `generate_report` function to change the color-coding levels.
	*   **Subject:** Adjust the subject to a more suitable description if neccessary

## Usage

Run the script from the command line, providing the year and month as arguments:

```bash
python s3_cost_reporter.py <year> <month>
