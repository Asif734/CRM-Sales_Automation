import os
from app.utils.llm_client import LLMClient
from app.emailer import Emailer
from app.responder import classify_response, simulate_response
from app.utils import read_leads, write_enriched, write_report
from app.templates import draft_email


DATA_DIR = os.getenv('DATA_DIR', '/app/data')
INPUT_FILE = os.path.join(DATA_DIR, 'leads.csv')
OUTPUT_FILE = os.path.join(DATA_DIR, 'enriched_leads.csv')
REPORTS_DIR = os.getenv('REPORTS_DIR', '/app/reports')
REPORT_FILE = os.path.join(REPORTS_DIR, 'campaign_summary.md')


SMTP_HOST = os.getenv('SMTP_HOST', 'mailhog')
SMTP_PORT = int(os.getenv('SMTP_PORT', '1025'))
FROM_NAME = os.getenv('FROM_NAME', 'Sales')
FROM_EMAIL = os.getenv('FROM_EMAIL', 'no-reply@example.com')




def run_pipeline():
    print('Starting pipeline...')
    df = read_leads(INPUT_FILE)
    print(f'Read {len(df)} leads')


    llm = LLMClient(provider=os.getenv('LLM_PROVIDER', 'mock'))
    emailer = Emailer(host=SMTP_HOST, port=SMTP_PORT, from_name=FROM_NAME, from_email=FROM_EMAIL)


    enriched_rows = []
    sent = 0
    responses = []


    for idx, row in df.iterrows():
        lead = row.to_dict()
        # Ensure required keys
        lead['name'] = lead.get('name') or 'Friend'
        lead['company'] = lead.get('company') or ''


        # Enrich with LLM
        enrichment = llm.enrich_lead(lead)
        lead.update(enrichment)


        # Draft email
        subject, body = draft_email(lead)
        lead['email_subject'] = subject
        lead['email_body'] = body


        # Send email
        try:
            emailer.send(to_email=lead.get('email'), to_name=lead.get('name'), subject=subject, body=body)
            lead['email_sent'] = True
            sent += 1
        except Exception as e:
            lead['email_sent'] = False
            lead['send_error'] = str(e)


        # Simulate response and classify
        resp = simulate_response(lead)
        cls = classify_response(resp)
        lead['response_text'] = resp
        lead['response_class'] = cls
        responses.append(cls)


        enriched_rows.append(lead)


    out_df = pd.DataFrame(enriched_rows)
    write_enriched(out_df, OUTPUT_FILE)


    # Summarize
    write_report(out_df, REPORT_FILE)


    print('Pipeline finished.')
    print(f'Emails sent: {sent}')




if __name__ == '__main__':
   run_pipeline()