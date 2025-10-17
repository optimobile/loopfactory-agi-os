"""
Content Generation System
Automatically generates blog posts and social media content for all 11 companies

Author: Manus AI
Date: October 17, 2025
"""

import os
import json
from datetime import datetime, timedelta
from typing import List, Dict
from openai import OpenAI

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

class ContentGenerator:
    """Generate blog posts and social media content"""
    
    def __init__(self, model: str = "gpt-4"):
        self.model = model
        self.client = client
    
    # ========================================================================
    # BLOG POST GENERATION
    # ========================================================================
    
    def generate_blog_post(self, company_name: str, industry: str, topic: str = None) -> Dict:
        """Generate a complete blog post"""
        
        # Generate topic if not provided
        if not topic:
            topic = self._generate_blog_topic(company_name, industry)
        
        # Generate content
        prompt = f"""Write a comprehensive, SEO-optimized blog post for {company_name}, 
a company in the {industry} industry.

Topic: {topic}

Requirements:
- 1200-1500 words
- Engaging introduction
- Clear headings and subheadings
- Actionable insights
- Strong conclusion with CTA
- SEO-friendly
- Professional tone

Format as JSON with:
- title: string
- slug: string (URL-friendly)
- excerpt: string (150 characters)
- content: string (full markdown content)
- seo_title: string
- seo_description: string
- keywords: array of strings
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an expert content writer specializing in technical and industry-specific blog posts."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        blog_post = json.loads(response.choices[0].message.content)
        blog_post["author_name"] = "AI Assistant"
        blog_post["published_at"] = datetime.now().isoformat()
        
        return blog_post
    
    def _generate_blog_topic(self, company_name: str, industry: str) -> str:
        """Generate a relevant blog topic"""
        prompt = f"""Generate a compelling blog post topic for {company_name}, 
a company in the {industry} industry.

The topic should be:
- Relevant to the industry
- Valuable to the target audience
- SEO-friendly
- Timely and engaging

Return only the topic title, nothing else."""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a content strategist."},
                {"role": "user", "content": prompt}
            ]
        )
        
        return response.choices[0].message.content.strip()
    
    def generate_blog_calendar(self, company_name: str, industry: str, weeks: int = 4) -> List[Dict]:
        """Generate a content calendar for blog posts"""
        prompt = f"""Create a {weeks}-week content calendar for {company_name}, 
a company in the {industry} industry.

Generate {weeks * 3} blog post topics (3 per week).

Each topic should be:
- Relevant to the industry
- Valuable to the target audience
- SEO-friendly
- Diverse in content type (how-to, listicle, case study, etc.)

Format as JSON array with:
- week: number
- day: string (Monday, Wednesday, Friday)
- topic: string
- content_type: string (how-to, listicle, case_study, guide, etc.)
- target_keywords: array of strings
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a content strategist."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        return result.get("calendar", [])
    
    # ========================================================================
    # SOCIAL MEDIA GENERATION
    # ========================================================================
    
    def generate_social_posts(self, company_name: str, industry: str, platform: str, count: int = 7) -> List[Dict]:
        """Generate social media posts for a platform"""
        
        platform_specs = {
            "twitter": {"max_length": 280, "hashtags": 2},
            "linkedin": {"max_length": 1300, "hashtags": 3},
            "facebook": {"max_length": 500, "hashtags": 2},
            "instagram": {"max_length": 2200, "hashtags": 10}
        }
        
        specs = platform_specs.get(platform.lower(), platform_specs["twitter"])
        
        prompt = f"""Generate {count} engaging social media posts for {company_name}, 
a company in the {industry} industry, for {platform}.

Requirements:
- Platform: {platform}
- Max length: {specs['max_length']} characters
- Include {specs['hashtags']} relevant hashtags
- Engaging and valuable content
- Mix of content types (tips, questions, facts, promotions)
- Professional tone

Format as JSON array with:
- content: string (the post text)
- hashtags: array of strings
- post_type: string (tip, question, fact, promotion, etc.)
- best_time: string (morning, afternoon, evening)
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a social media marketing expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        result = json.loads(response.choices[0].message.content)
        posts = result.get("posts", [])
        
        # Add scheduling
        base_date = datetime.now()
        for i, post in enumerate(posts):
            post["scheduled_for"] = (base_date + timedelta(days=i)).isoformat()
            post["platform"] = platform
            post["status"] = "scheduled"
        
        return posts
    
    def generate_week_of_social_content(self, company_name: str, industry: str) -> Dict:
        """Generate a week's worth of social media content across all platforms"""
        platforms = ["twitter", "linkedin", "facebook", "instagram"]
        
        content = {}
        for platform in platforms:
            content[platform] = self.generate_social_posts(
                company_name=company_name,
                industry=industry,
                platform=platform,
                count=7  # One per day
            )
        
        return content
    
    # ========================================================================
    # EMAIL CAMPAIGNS
    # ========================================================================
    
    def generate_email_campaign(self, company_name: str, industry: str, campaign_type: str = "newsletter") -> Dict:
        """Generate an email campaign"""
        
        prompt = f"""Create an email campaign for {company_name}, 
a company in the {industry} industry.

Campaign type: {campaign_type}

Requirements:
- Compelling subject line
- Engaging preview text
- Well-structured email body (HTML)
- Clear CTA
- Professional tone

Format as JSON with:
- subject: string
- preview_text: string
- body_html: string
- body_text: string (plain text version)
- cta_text: string
- cta_url: string
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are an email marketing expert."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    # ========================================================================
    # OUTREACH MESSAGES
    # ========================================================================
    
    def generate_outreach_message(
        self,
        company_name: str,
        industry: str,
        recipient_name: str,
        recipient_company: str,
        context: str = None
    ) -> Dict:
        """Generate a personalized outreach message"""
        
        context_str = f"\nContext: {context}" if context else ""
        
        prompt = f"""Write a personalized outreach email for {company_name}, 
a company in the {industry} industry.

Recipient: {recipient_name} at {recipient_company}{context_str}

Requirements:
- Personalized and relevant
- Clear value proposition
- Not salesy or pushy
- Professional tone
- Clear CTA

Format as JSON with:
- subject: string
- body: string
- follow_up_subject: string (for follow-up email)
- follow_up_body: string
"""
        
        response = self.client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": "You are a B2B outreach specialist."},
                {"role": "user", "content": prompt}
            ],
            response_format={"type": "json_object"}
        )
        
        return json.loads(response.choices[0].message.content)
    
    # ========================================================================
    # BATCH GENERATION
    # ========================================================================
    
    def generate_all_content_for_company(self, company_data: Dict) -> Dict:
        """Generate all content types for a company"""
        company_name = company_data["name"]
        industry = company_data["industry"]
        
        print(f"Generating content for {company_name}...")
        
        # Blog posts (3 for the week)
        blog_calendar = self.generate_blog_calendar(company_name, industry, weeks=1)
        blog_posts = []
        for item in blog_calendar[:3]:  # First 3 topics
            blog_post = self.generate_blog_post(company_name, industry, item["topic"])
            blog_posts.append(blog_post)
            print(f"  Generated blog post: {blog_post['title']}")
        
        # Social media (week of content)
        social_content = self.generate_week_of_social_content(company_name, industry)
        print(f"  Generated {sum(len(posts) for posts in social_content.values())} social posts")
        
        # Email campaign
        email_campaign = self.generate_email_campaign(company_name, industry)
        print(f"  Generated email campaign: {email_campaign['subject']}")
        
        return {
            "company": company_name,
            "blog_posts": blog_posts,
            "social_content": social_content,
            "email_campaign": email_campaign,
            "generated_at": datetime.now().isoformat()
        }


# Example usage
if __name__ == "__main__":
    generator = ContentGenerator()
    
    # Example company
    company = {
        "name": "KoiKeeper AI",
        "industry": "Koi Pond Management"
    }
    
    # Generate all content
    content = generator.generate_all_content_for_company(company)
    
    # Save to file
    output_file = f"/home/ubuntu/loopfactory-agi-os/data/content_{company['name'].replace(' ', '_').lower()}.json"
    with open(output_file, 'w') as f:
        json.dump(content, f, indent=2)
    
    print(f"\nContent saved to {output_file}")

