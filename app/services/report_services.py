from typing import List
from app.models import Lead, CampaignStats
from app.config import Settings
from datetime import datetime
from collections import Counter
from app.utils.logger import setup_logger
import os

logger = setup_logger(__name__)


class ReportService:
    """Generate campaign summary reports"""
    
    def __init__(self, settings: Settings):
        self.settings = settings
    
    def generate_stats(self, leads: List[Lead]) -> CampaignStats:
        """Calculate campaign statistics"""
        
        total = len(leads)
        sent = sum(1 for l in leads if l.email_status == "sent")
        failed = sum(1 for l in leads if l.email_status == "failed")
        
        high = sum(1 for l in leads if l.priority == "High")
        medium = sum(1 for l in leads if l.priority == "Medium")
        low = sum(1 for l in leads if l.priority == "Low")
        
        # Top personas
        personas = [l.ai_persona for l in leads if l.ai_persona]
        persona_counts = Counter(personas)
        top_personas = dict(persona_counts.most_common(5))
        
        # Top industries
        industries = [l.industry for l in leads]
        industry_counts = Counter(industries)
        top_industries = dict(industry_counts.most_common(5))
        
        return CampaignStats(
            total_leads=total,
            emails_sent=sent,
            emails_failed=failed,
            high_priority=high,
            medium_priority=medium,
            low_priority=low,
            top_personas=top_personas,
            top_industries=top_industries
        )
    
    async def generate_report(self, leads: List[Lead]) -> str:
        """Generate markdown campaign report"""
        
        stats = self.generate_stats(leads)
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        report_path = os.path.join(self.settings.report_output_dir, f"campaign_{timestamp}.md")
        
        total = stats.total_leads
        
        report = f"""# 📊 AI Sales Campaign Summary Report
**Generated:** {datetime.now().strftime("%Y-%m-%d %H:%M:%S")}

---

## 📈 Campaign Overview

| Metric | Count | Percentage |
|--------|-------|------------|
| **Total Leads Processed** | {total} | 100% |
| **Emails Successfully Sent** | {stats.emails_sent} | {(stats.emails_sent/total*100):.1f}% |
| **Emails Failed** | {stats.emails_failed} | {(stats.emails_failed/total*100):.1f}% |

---

## 🎯 Lead Prioritization

| Priority | Count | Percentage |
|----------|-------|------------|
| 🔴 **High Priority** | {stats.high_priority} | {(stats.high_priority/total*100):.1f}% |
| 🟡 **Medium Priority** | {stats.medium_priority} | {(stats.medium_priority/total*100):.1f}% |
| 🟢 **Low Priority** | {stats.low_priority} | {(stats.low_priority/total*100):.1f}% |

---

## 👥 Top Buyer Personas Identified

"""
        for persona, count in stats.top_personas.items():
            pct = (count / total * 100)
            report += f"- **{persona}**: {count} leads ({pct:.1f}%)\n"
        
        report += f"""
---

## 🏢 Industry Breakdown

"""
        for industry, count in stats.top_industries.items():
            pct = (count / total * 100)
            report += f"- **{industry}**: {count} leads ({pct:.1f}%)\n"
        
        report += f"""
---

## 💡 AI-Generated Insights

### Key Findings:
1. **High-Value Segment**: {stats.high_priority} leads identified as high-priority based on role, company size, and industry fit
2. **Top Persona**: {list(stats.top_personas.keys())[0] if stats.top_personas else 'N/A'} represents the largest buyer persona group
3. **Industry Focus**: {list(stats.top_industries.keys())[0] if stats.top_industries else 'N/A'} industry shows strongest representation

### Recommendations:
- Follow up quickly with high-priority leads (typically respond within 24 hours)
- Personalize messaging based on identified buyer personas
- Consider industry-specific value propositions for concentrated segments
- Monitor email engagement metrics for optimization

---

## 🚀 Next Steps

1. **Check MailHog**: View sent emails at http://localhost:8025
2. **Review CSV**: Check `data/leads_processed.csv` for all lead data
3. **Follow Up**: Prioritize high-scoring leads for immediate outreach
4. **Optimize**: Use insights to refine future campaigns

---

**Campaign Powered By:** AI Sales Campaign CRM v1.0  
**Report Location:** `{report_path}`
"""
        
        try:
            os.makedirs(self.settings.report_output_dir, exist_ok=True)
            with open(report_path, 'w') as f:
                f.write(report)
            logger.info(f"✓ Report generated: {report_path}")
        except Exception as e:
            logger.error(f"Failed to write report: {e}")
        
        return report_path