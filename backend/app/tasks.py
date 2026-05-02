import os
import json
import logging
import time
from typing import Dict, Any, Optional
from openai import OpenAI
from .celery_config import celery_app
from .core.telemetry import get_tracer, track_gpt_request, celery_task_duration, error_counter

logger = logging.getLogger(__name__)

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Get tracer for custom spans
tracer = get_tracer("resume_tasks")

@celery_app.task(bind=True, name="generate_resume")
def generate_resume_task(self, resume_data: Dict[str, Any], job_analysis: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate a tailored resume and cover letter based on resume data and job analysis.
    
    Args:
        resume_data: Dictionary containing structured resume information
        job_analysis: Dictionary containing job description analysis results
    
    Returns:
        Dictionary containing generated resume content and cover letter
    """
    task_id = self.request.id
    start_time = time.time()
    
    # Create a span for the entire task
    with tracer.start_as_current_span(f"celery.task.generate_resume") as task_span:
        task_span.set_attribute("celery.task_id", task_id)
        task_span.set_attribute("celery.task_name", "generate_resume")
        
        self.update_state(state="PROCESSING", meta={"status": "Processing resume generation"})
        
        try:
            # Extract relevant information from inputs
            skills = resume_data.get("skills", [])
            experience = resume_data.get("experience", [])
            education = resume_data.get("education", [])
            
            job_skills = job_analysis.get("skills", [])
            job_tools = job_analysis.get("tools", [])
            job_methodologies = job_analysis.get("methodologies", [])
            job_experience_level = job_analysis.get("experience_level", "not specified")
            
            # Create prompt for resume content generation
            with tracer.start_as_current_span("create_resume_prompt"):
                resume_prompt = create_resume_prompt(
                    resume_data=resume_data,
                    job_skills=job_skills,
                    job_tools=job_tools,
                    job_methodologies=job_methodologies,
                    job_experience_level=job_experience_level
                )
            
            # Generate tailored resume content
            self.update_state(state="GENERATING_RESUME", meta={"status": "Generating resume content"})
            with tracer.start_as_current_span("generate_resume_content"):
                resume_content = generate_content_with_gpt4(resume_prompt)
            
            # Create prompt for cover letter generation
            with tracer.start_as_current_span("create_cover_letter_prompt"):
                cover_letter_prompt = create_cover_letter_prompt(
                    resume_data=resume_data,
                    job_analysis=job_analysis
                )
            
            # Generate tailored cover letter
            self.update_state(state="GENERATING_COVER_LETTER", meta={"status": "Generating cover letter"})
            with tracer.start_as_current_span("generate_cover_letter"):
                cover_letter = generate_content_with_gpt4(cover_letter_prompt)
            
            # Return the generated content
            result = {
                "task_id": task_id,
                "status": "completed",
                "resume_content": resume_content,
                "cover_letter": cover_letter
            }
            
            # Record task duration
            duration = time.time() - start_time
            celery_task_duration.record(duration, {"task_name": "generate_resume"})
            
            return result
            
        except Exception as e:
            error_message = str(e)
            logger.error(f"Error generating resume: {error_message}")
            
            # Record error in metrics and span
            error_counter.add(1, {"error_type": "resume_generation"})
            task_span.record_exception(e)
            
            self.update_state(
                state="FAILURE",
                meta={"status": "Failed", "error": error_message}
            )
            raise

def create_resume_prompt(resume_data: Dict[str, Any], job_skills: list, job_tools: list, 
                        job_methodologies: list, job_experience_level: str) -> str:
    """
    Create a prompt for GPT-4 to generate a tailored resume.
    """
    name = resume_data.get("name", "")
    current_experience = resume_data.get("experience", [])
    
    # Format experience for the prompt
    experience_text = ""
    for exp in current_experience:
        experience_text += f"- {exp.get('title', '')} at {exp.get('company', '')}, {exp.get('start_date', '')} to {exp.get('end_date', 'Present')}\n"
        experience_text += f"  {exp.get('description', '')}\n\n"
    
    # Combine all job requirements
    all_job_keywords = job_skills + job_tools + job_methodologies
    job_keywords_text = ", ".join(all_job_keywords)
    
    prompt = f"""
    You are an expert resume writer with years of experience in optimizing resumes for ATS systems and hiring managers.
    
    TASK: Rewrite the following resume experience sections to be more impactful, ATS-optimized, and tailored to the job requirements.
    
    RESUME OWNER: {name}
    
    CURRENT EXPERIENCE:
    {experience_text}
    
    JOB REQUIREMENTS:
    - Required skills and keywords: {job_keywords_text}
    - Experience level: {job_experience_level}
    
    INSTRUCTIONS:
    1. Rewrite each experience bullet point to be more impactful and achievement-oriented
    2. Quantify achievements wherever possible (e.g., increased efficiency by 30%)
    3. Incorporate relevant keywords from the job requirements naturally
    4. Use strong action verbs at the beginning of each bullet point
    5. Focus on results and impact, not just responsibilities
    6. Ensure content is ATS-friendly with standard formatting
    7. Maintain professional language and tone
    8. Keep the same job titles, companies, and dates
    
    FORMAT:
    For each position, provide:
    - Job Title, Company, Date Range (unchanged)
    - 3-5 bullet points of achievements and responsibilities
    
    OUTPUT FORMAT:
    Return the rewritten experience sections in a clean, professional format ready to be included in a resume.
    """
    
    return prompt

def create_cover_letter_prompt(resume_data: Dict[str, Any], job_analysis: Dict[str, Any]) -> str:
    """
    Create a prompt for GPT-4 to generate a tailored cover letter.
    """
    name = resume_data.get("name", "")
    summary = resume_data.get("summary", "")
    
    job_skills = job_analysis.get("skills", [])
    job_tools = job_analysis.get("tools", [])
    job_methodologies = job_analysis.get("methodologies", [])
    
    # Combine all job requirements
    all_job_keywords = job_skills + job_tools + job_methodologies
    job_keywords_text = ", ".join(all_job_keywords)
    
    prompt = f"""
    You are an expert cover letter writer with years of experience in crafting compelling, personalized cover letters.
    
    TASK: Write a professional cover letter for {name} that highlights their relevant skills and experience for a position requiring the following skills and tools.
    
    ABOUT THE APPLICANT:
    {summary}
    
    JOB REQUIREMENTS:
    - Required skills and keywords: {job_keywords_text}
    
    INSTRUCTIONS:
    1. Write a compelling, personalized cover letter (300-400 words)
    2. Address why the applicant is interested in this type of role
    3. Highlight 2-3 most relevant achievements that demonstrate required skills
    4. Naturally incorporate relevant keywords from the job requirements
    5. Include a strong opening and closing paragraph
    6. Maintain professional language and tone
    7. Focus on how the applicant can add value to the company
    8. Keep the letter concise, engaging, and tailored to the job requirements
    
    OUTPUT FORMAT:
    Return a complete, ready-to-use cover letter with appropriate greeting and signature.
    """
    
    return prompt

def generate_content_with_gpt4(prompt: str) -> str:
    """
    Generate content using OpenAI's GPT-4 model.
    """
    try:
        start_time = time.time()
        
        with tracer.start_as_current_span("openai_gpt4_request") as span:
            span.set_attribute("prompt.length", len(prompt))
            
            response = client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": "You are an expert resume and cover letter writer."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            content = response.choices[0].message.content
            
            # Calculate duration
            duration = time.time() - start_time
            
            # Extract token counts
            prompt_tokens = response.usage.prompt_tokens
            completion_tokens = response.usage.completion_tokens
            
            # Record metrics
            span.set_attribute("tokens.prompt", prompt_tokens)
            span.set_attribute("tokens.completion", completion_tokens)
            span.set_attribute("response.duration", duration)
            
            # Track GPT request metrics including cost calculation
            track_gpt_request(prompt_tokens, completion_tokens, "gpt-4", duration)
            
            return content
            
    except Exception as e:
        error_message = str(e)
        logger.error(f"Error calling OpenAI API: {error_message}")
        
        # Record error in metrics
        error_counter.add(1, {"error_type": "openai_api"})
        
        # Re-raise the exception
        raise