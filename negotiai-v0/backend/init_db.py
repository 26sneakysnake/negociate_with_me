# backend/init_db.py
from database import engine, Base, SessionLocal
from db_models import ContextTemplate
import json

def create_tables():
    """Create all tables"""
    print("Creating database tables...")
    Base.metadata.create_all(bind=engine)
    print("✅ Tables created successfully!")

def load_templates():
    """Load default context templates"""
    print("Loading context templates...")

    templates = [
        {
            "id": "saas-enterprise",
            "name": "SaaS Enterprise License",
            "category": "saas",
            "description": "Negotiation for enterprise software licensing",
            "icon": "💻",
            "context_template": """SaaS Platform License Negotiation

Company: [Company Name]
Product: [Your SaaS Product]
Current Situation:
- Prospect interested in annual/multi-year license
- Their stated budget: [Budget Range]
- Your standard pricing: [Your Price]
- Competition: [Competitor Name] at [Competitor Price]
- Your advantages: [List advantages - support, features, implementation speed]

Key Decision Maker: [Name, Title]
Timeline: [When they want to close]
Additional Context: [Any relevant details about their needs, pain points, or past vendor experiences]""",
            "objective_template": "Secure [Amount]€ annual contract",
            "minimum_template": "Not below [Minimum]€"
        },
        {
            "id": "real-estate-purchase",
            "name": "Achat Immobilier / Real Estate Purchase",
            "category": "immobilier",
            "description": "Negotiation for property purchase",
            "icon": "🏠",
            "context_template": """Négociation Achat Immobilier

Propriété: [Type et adresse]
Prix demandé: [Prix du vendeur]
Votre budget maximum: [Votre budget]

Situation du bien:
- État: [Bon état / Travaux à prévoir]
- Temps sur le marché: [Depuis quand en vente]
- Situation du vendeur: [Pressé de vendre / Pas pressé]
- Concurrence: [Nombre d'acheteurs potentiels]

Vos atouts:
- [Ex: Financement assuré, achat comptant]
- [Ex: Flexibilité sur la date de clôture]
- [Ex: Pas de bien à vendre]

Contraintes:
- [Ex: Besoin d'emménager avant une certaine date]
- [Ex: Travaux importants à prévoir]""",
            "objective_template": "Acheter à [Prix cible]€",
            "minimum_template": "Ne pas dépasser [Prix maximum]€"
        },
        {
            "id": "salary-negotiation",
            "name": "Salary Negotiation",
            "category": "salaire",
            "description": "Salary negotiation for job offer or raise",
            "icon": "💰",
            "context_template": """Salary Negotiation

Position: [Job Title]
Company: [Company Name]
Current Offer: [Offered Salary]
Market Rate: [Industry Average for this role]

Your Background:
- Years of experience: [X years]
- Key skills: [List relevant skills]
- Recent achievements: [Notable accomplishments]
- Competing offers: [If any]

Company Context:
- Company size: [Startup / Scale-up / Enterprise]
- Funding status: [If relevant]
- Urgency to fill role: [High / Medium / Low]

Additional Considerations:
- Benefits: [Health insurance, stock options, bonus, etc.]
- Remote work policy: [Fully remote / Hybrid / On-site]
- Career growth opportunities: [Promotion path, learning budget]""",
            "objective_template": "Secure [Target Salary]€ annual salary + [Benefits]",
            "minimum_template": "Not below [Minimum Salary]€"
        },
        {
            "id": "freelance-contract",
            "name": "Freelance / Consulting Contract",
            "category": "saas",
            "description": "Freelance or consulting service agreement",
            "icon": "📝",
            "context_template": """Freelance / Consulting Contract Negotiation

Client: [Company Name]
Project: [Project Description]
Proposed Rate: [Client's budget or initial offer]
Market Rate: [Your usual rate or industry average]

Project Scope:
- Duration: [Estimated timeline]
- Deliverables: [What you'll deliver]
- Complexity: [Technical complexity, risk factors]
- Time commitment: [Hours per week / month]

Your Value Proposition:
- Expertise: [Your specialized skills]
- Track record: [Relevant past projects]
- Availability: [When you can start]

Client Context:
- Budget flexibility: [Constrained / Flexible]
- Project urgency: [Deadline pressure]
- Potential for ongoing work: [One-off / Long-term relationship]""",
            "objective_template": "Secure [Rate]€/hour or [Project Budget]€ fixed price",
            "minimum_template": "Not below [Minimum Rate]€/hour"
        },
        {
            "id": "vendor-contract",
            "name": "Vendor / Supplier Contract",
            "category": "saas",
            "description": "Negotiation with suppliers or vendors",
            "icon": "🤝",
            "context_template": """Vendor / Supplier Contract Negotiation

Vendor: [Company Name]
Product/Service: [What you're buying]
Their Quote: [Initial price]
Your Budget: [Your target price]

Volume & Terms:
- Quantity: [Annual volume or units]
- Contract length: [1 year / Multi-year]
- Payment terms: [Net 30 / Net 60 / Upfront]

Your Leverage:
- Competition: [Alternative vendors]
- Volume potential: [Current + future growth]
- Long-term partnership value: [Repeat business potential]

Their Position:
- Market position: [Leader / Challenger / Niche]
- Capacity: [Can they handle your volume]
- Flexibility: [How much room to negotiate]""",
            "objective_template": "Secure [Target Price]€ with [Desired Payment Terms]",
            "minimum_template": "Not above [Maximum Price]€"
        }
    ]

    db = SessionLocal()
    try:
        # Check if templates already exist
        existing = db.query(ContextTemplate).count()
        if existing > 0:
            print(f"⚠️ {existing} templates already exist, skipping...")
            return

        # Insert templates
        for template_data in templates:
            template = ContextTemplate(**template_data)
            db.add(template)

        db.commit()
        print(f"✅ Loaded {len(templates)} context templates!")

    except Exception as e:
        print(f"❌ Error loading templates: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    create_tables()
    load_templates()
    print("\n✅ Database initialization complete!")
