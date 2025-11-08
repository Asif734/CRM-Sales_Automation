"""
Email templates module - pre-built and customizable email templates
"""
from typing import Dict, Optional, List
from string import Template
from enum import Enum
from app.models import Lead


class TemplateType(str, Enum):
    """Template categories"""
    COLD_OUTREACH = "cold_outreach"
    FOLLOW_UP = "follow_up"
    DEMO_REQUEST = "demo_request"
    MEETING_CONFIRMATION = "meeting_confirmation"
    THANK_YOU = "thank_you"
    RE_ENGAGEMENT = "re_engagement"
    PRODUCT_ANNOUNCEMENT = "product_announcement"
    CUSTOM = "custom"


class EmailTemplate:
    """Email template with variables"""
    
    def __init__(
        self, 
        name: str,
        template_type: TemplateType,
        subject_template: str,
        body_template: str,
        description: Optional[str] = None
    ):
        self.name = name
        self.template_type = template_type
        self.subject_template = Template(subject_template)
        self.body_template = Template(body_template)
        self.description = description or ""
    
    def render(self, variables: Dict[str, str]) -> Dict[str, str]:
        """
        Render template with variables
        
        Args:
            variables: Dict of variable names to values
        
        Returns:
            Dict with 'subject' and 'body'
        """
        try:
            subject = self.subject_template.safe_substitute(variables)
            body = self.body_template.safe_substitute(variables)
            
            return {
                "subject": subject,
                "body": body
            }
        except Exception as e:
            raise ValueError(f"Template rendering failed: {e}")
    
    def render_for_lead(self, lead: Lead, **kwargs) -> Dict[str, str]:
        """
        Render template for a specific lead
        
        Args:
            lead: Lead object
            **kwargs: Additional variables to override/add
        
        Returns:
            Dict with 'subject' and 'body'
        """
        # Build variables from lead
        variables = {
            'first_name': lead.name.split()[0],
            'full_name': lead.name,
            'email': lead.email,
            'company': lead.company,
            'role': lead.role,
            'industry': lead.industry,
            'company_size': lead.company_size,
            'persona': lead.ai_persona or 'Professional',
            'priority': lead.priority or 'Medium',
        }
        
        # Add custom variables
        variables.update(kwargs)
        
        return self.render(variables)


class TemplateLibrary:
    """Collection of email templates"""
    
    def __init__(self):
        self.templates: Dict[str, EmailTemplate] = {}
        self._load_default_templates()
    
    def _load_default_templates(self):
        """Load default template collection"""
        
        # Template 1: Cold Outreach - C-Level
        self.add_template(EmailTemplate(
            name="cold_outreach_clevel",
            template_type=TemplateType.COLD_OUTREACH,
            subject_template="Quick question about ${company}'s growth",
            body_template="""Hi ${first_name},

I noticed ${company} is scaling in the ${industry} space—congrats on the momentum!

Many ${role}s we work with face challenges around operational efficiency as they grow. We've helped similar companies reduce costs by 30% while scaling faster.

Would you be open to a brief conversation about how we might support ${company}'s goals?

Best regards,
Your Sales Team

P.S. No pressure—just wanted to share what's working for others in ${industry}.""",
            description="Cold outreach for C-level executives"
        ))
        
        # Template 2: Cold Outreach - Technical
        self.add_template(EmailTemplate(
            name="cold_outreach_technical",
            template_type=TemplateType.COLD_OUTREACH,
            subject_template="AI automation for ${company}'s tech stack",
            body_template="""Hi ${first_name},

As ${role} at ${company}, you're probably dealing with complex workflows and integration challenges.

We've built an AI platform that helps teams like yours:
• Automate repetitive tasks
• Integrate seamlessly with existing tools
• Scale without adding headcount

${company} in ${industry} could see immediate impact.

Interested in a quick demo? Happy to show you what's possible.

Cheers,
Your Sales Team""",
            description="Technical outreach for engineering leaders"
        ))
        
        # Template 3: Follow-up
        self.add_template(EmailTemplate(
            name="follow_up_general",
            template_type=TemplateType.FOLLOW_UP,
            subject_template="Following up: ${company} + AI automation",
            body_template="""Hi ${first_name},

Wanted to circle back on my previous email about helping ${company} streamline operations.

I completely understand you're busy—that's exactly why automation matters. 

Quick question: What's your biggest operational bottleneck right now?

If now isn't the right time, totally fine. Just let me know when makes sense.

Best,
Your Sales Team""",
            description="General follow-up email"
        ))
        
        # Template 4: Meeting Request
        self.add_template(EmailTemplate(
            name="meeting_request",
            template_type=TemplateType.DEMO_REQUEST,
            subject_template="15-min demo for ${company}?",
            body_template="""Hi ${first_name},

Thanks for your interest! I'd love to show you what we can do for ${company}.

How about a quick 15-minute demo? I'll show you:
1. How we solve ${industry}-specific challenges
2. Real results from similar companies
3. Custom solution for ${company}'s needs

Here's my calendar link: [LINK]

Or let me know what works for you!

Looking forward to it,
Your Sales Team""",
            description="Meeting/demo request"
        ))
        
        # Template 5: Re-engagement
        self.add_template(EmailTemplate(
            name="re_engagement",
            template_type=TemplateType.RE_ENGAGEMENT,
            subject_template="Still relevant for ${company}?",
            body_template="""Hi ${first_name},

I reached out a while back about helping ${company} with AI-powered automation.

Wasn't sure if:
a) Timing wasn't right
b) Not the right solution
c) My email got buried (happens to me too!)

If you're still exploring ways to streamline operations, I'd love to reconnect. If not, no worries at all—just let me know and I'll stop bothering you!

What do you think?

Best,
Your Sales Team""",
            description="Re-engage cold leads"
        ))
        
        # Template 6: Thank You
        self.add_template(EmailTemplate(
            name="thank_you_meeting",
            template_type=TemplateType.THANK_YOU,
            subject_template="Thanks for your time, ${first_name}!",
            body_template="""Hi ${first_name},

Really enjoyed our conversation about ${company}'s goals today.

Quick recap of what we discussed:
• ${point1}
• ${point2}
• ${point3}

Next steps:
${next_steps}

I'll send over ${deliverable} by ${deadline}.

Feel free to reach out with any questions!

Best,
Your Sales Team""",
            description="Post-meeting thank you"
        ))
        
        # Template 7: Product Announcement
        self.add_template(EmailTemplate(
            name="product_announcement",
            template_type=TemplateType.PRODUCT_ANNOUNCEMENT,
            subject_template="New feature for ${industry} teams",
            body_template="""Hi ${first_name},

Exciting news for ${industry} leaders!

We just launched a new feature that specifically helps companies like ${company}:

${feature_highlight}

Early adopters are seeing:
• ${benefit1}
• ${benefit2}
• ${benefit3}

Want to be among the first to try it? Reply and I'll get you early access.

Best,
Your Sales Team""",
            description="Product update announcement"
        ))
        
        # Template 8: Value Proposition
        self.add_template(EmailTemplate(
            name="value_proposition",
            template_type=TemplateType.COLD_OUTREACH,
            subject_template="3 ways ${company} can scale faster",
            body_template="""Hi ${first_name},

Quick note: I've been researching ${company} and the ${industry} space.

Here are 3 ways companies like yours are accelerating growth:

1. **Automate manual workflows** - Save 20+ hours/week
2. **AI-powered insights** - Make data-driven decisions faster
3. **Seamless integrations** - Connect your entire stack

We've helped ${similar_company} achieve these results in just 60 days.

Worth a conversation? Let me know if you'd like to see how.

Cheers,
Your Sales Team""",
            description="Value-focused cold outreach"
        ))
    
    def add_template(self, template: EmailTemplate):
        """Add template to library"""
        self.templates[template.name] = template
    
    def get_template(self, name: str) -> Optional[EmailTemplate]:
        """Get template by name"""
        return self.templates.get(name)
    
    def get_templates_by_type(self, template_type: TemplateType) -> List[EmailTemplate]:
        """Get all templates of a specific type"""
        return [t for t in self.templates.values() if t.template_type == template_type]
    
    def list_templates(self) -> List[Dict[str, str]]:
        """List all available templates"""
        return [
            {
                "name": t.name,
                "type": t.template_type,
                "description": t.description
            }
            for t in self.templates.values()
        ]
    
    def render_template(
        self, 
        template_name: str, 
        lead: Lead, 
        **kwargs
    ) -> Dict[str, str]:
        """
        Render a template for a lead
        
        Args:
            template_name: Name of template to use
            lead: Lead object
            **kwargs: Additional variables
        
        Returns:
            Dict with 'subject' and 'body'
        """
        template = self.get_template(template_name)
        
        if not template:
            raise ValueError(f"Template '{template_name}' not found")
        
        return template.render_for_lead(lead, **kwargs)


# Global template library instance
template_library = TemplateLibrary()


# Helper functions
def get_template(name: str) -> Optional[EmailTemplate]:
    """Get a template by name"""
    return template_library.get_template(name)


def render_template(template_name: str, lead: Lead, **kwargs) -> Dict[str, str]:
    """Render a template for a lead"""
    return template_library.render_template(template_name, lead, **kwargs)


def list_templates() -> List[Dict[str, str]]:
    """List all available templates"""
    return template_library.list_templates()


# Example usage in comments:
"""
from app.templates import template_library, render_template

# List all templates
templates = template_library.list_templates()

# Render template for a lead
email = render_template(
    "cold_outreach_clevel",
    lead=some_lead,
    sender_name="John Smith"
)

# Use rendered email
print(email['subject'])
print(email['body'])

# Get templates by type
cold_outreach_templates = template_library.get_templates_by_type(TemplateType.COLD_OUTREACH)

# Add custom template
custom = EmailTemplate(
    name="my_custom",
    template_type=TemplateType.CUSTOM,
    subject_template="Custom subject for ${company}",
    body_template="Custom body for ${first_name}...",
    description="My custom template"
)
template_library.add_template(custom)
"""