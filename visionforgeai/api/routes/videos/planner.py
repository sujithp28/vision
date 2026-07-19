"""Video Planner API Endpoints.

This module provides endpoints for planning video content using AI assistance.
"""

from typing import List, Optional
from fastapi import APIRouter, HTTPException, status
from pydantic import BaseModel, Field

from visionforgeai.services.llm_service import get_llm_service

router = APIRouter(prefix="/video/planner", tags=["video-planning"])


class VideoPlannerRequest(BaseModel):
    """Request model for video planning."""
    prompt: str = Field(..., description="The video topic or idea to plan")
    target_audience: Optional[str] = Field(
        None, description="Target audience for the video (e.g., 'children aged 5-8')"
    )
    video_length: Optional[int] = Field(
        None, description="Desired video length in minutes"
    )
    educational_goal: Optional[str] = Field(
        None, description="Specific educational goal or learning objective"
    )
    include_activities: bool = Field(
        default=False, description="Whether to include suggested activities"
    )
    include_assessment: bool = Field(
        default=False, description="Whether to include assessment ideas"
    )


class VideoPlannerResponse(BaseModel):
    """Response model for video planning."""
    video_plan: str = Field(..., description="The generated video plan")
    prompt_used: str = Field(..., description="The prompt that was used for generation")
    model_used: str = Field(..., description="The LLM model used for generation")
    tokens_used: Optional[int] = Field(
        None, description="Number of tokens consumed"
    )


# Prompt templates for different educational contexts
PROMPT_TEMPLATES = {
    "educational_kids": """
Create a detailed video plan for an educational video for children aged {age_group} about the topic: {topic}.

The video should be approximately {duration} minutes long and focus on {learning_objective}.

Please include:
1. Hook/Introduction (how to grab children's attention)
2. Main content segments with clear explanations
3. Visual suggestions (animations, demonstrations, etc.)
4. Engagement techniques (questions, calls-to-action)
5. Summary and call-to-action

{additional_sections}
""",
    "educational_general": """
Create a detailed video plan for an educational video about the topic: {topic}.

Target audience: {target_audience}
Video length: {video_length} minutes
Educational goal: {educational_goal}

Please include:
1. Engaging introduction
2. Main content broken into logical segments
3. Visual and audio suggestions
4. Interactive elements or demonstrations
5. Conclusion with key takeaways
6. {additional_sections}
""",
    "general": """
Create a comprehensive video plan for the topic: {topic}.

{additional_context}

Please provide:
1. Video concept and hook
2. Detailed outline with timestamps
3. Key points to cover
4. Visual and audio suggestions
5. Engagement strategies
6. Call-to-action
""",
}


def build_prompt(request: VideoPlannerRequest) -> str:
    """Build a prompt for video planning based on the request."""

    # Determine which template to use
    if request.target_audience and "children" in request.target_audience.lower():
        template_key = "educational_kids"
    elif request.target_audience or request.educational_goal:
        template_key = "educational_general"
    else:
        template_key = "general"

    template = PROMPT_TEMPLATES[template_key]

    # Build additional sections
    additional_sections = []
    if request.include_activities:
        additional_sections.append("Suggested hands-on activities or experiments")
    if request.include_assessment:
        additional_sections.append("Assessment ideas to check understanding")

    additional_sections_text = "\n".join(f"- {section}" for section in additional_sections) if additional_sections else "No additional sections requested"

    # Format the template based on the template key
    if template_key == "educational_kids":
        prompt = template.format(
            age_group=request.target_audience or "children",
            topic=request.prompt,
            duration=request.video_length or 5,
            learning_objective=request.educational_goal or "educational content",
            additional_sections=additional_sections_text
        )
    elif template_key == "educational_general":
        prompt = template.format(
            topic=request.prompt,
            target_audience=request.target_audience or "general audience",
            video_length=request.video_length or 5,
            educational_goal=request.educational_goal or "educational content",
            additional_sections=additional_sections_text
        )
    else:  # general
        additional_context = ""
        if request.target_audience:
            additional_content += f"Target audience: {request.target_audience}\n"
        if request.video_length:
            additional_content += f"Desired length: {request.video_length} minutes\n"
        if request.educational_goal:
            additional_content += f"Educational goal: {request.educational_goal}\n"
        if request.include_activities:
            additional_content += "Include suggestions for hands-on activities\n"
        if request.include_assessment:
            additional_content += "Include ideas for assessment or knowledge checks\n"

        # Fix the variable name - it should be additional_context, not additional_content
        # Actually, let's rewrite this part correctly
        additional_context = ""
        if request.target_audience:
            additional_context += f"Target audience: {request.target_audience}\n"
        if request.video_length:
            additional_context += f"Desired length: {request.video_length} minutes\n"
        if request.educational_goal:
            additional_context += f"Educational goal: {request.educational_goal}\n"
        if request.include_activities:
            additional_context += "Include suggestions for hands-on activities\n"
        if request.include_assessment:
            additional_context += "Include ideas for assessment or knowledge checks\n"

        prompt = template.format(
            topic=request.prompt,
            additional_context=additional_context.strip()
        )

    return prompt


@router.post("/", response_model=VideoPlannerResponse)
async def create_video_plan(request: VideoPlannerRequest):
    """Create a video plan using AI assistance.

    This endpoint takes a video topic/idea and generates a detailed plan
    including structure, content suggestions, and engagement strategies.
    """
    try:
        # Build the prompt using templates
        print("Building prompt...")
        prompt = build_prompt(request)
        print(f"Prompt: {prompt}")

        # Get LLM service
        llm_service = get_llm_service()

        # Generate the video plan
        video_plan = await llm_service.generate_text(
            prompt=prompt,
            max_tokens=1500,  # Allow for detailed plans
            temperature=0.7  # Balance creativity and coherence
        )

        # Get provider info for response
        provider_info = llm_service.get_provider_info()

        return VideoPlannerResponse(
            video_plan=video_plan.strip(),
            prompt_used=prompt,
            model_used=provider_info.get("model", "unknown"),
            tokens_used=None  # TODO: Extract from usage if available
        )

    except Exception as e:
        import traceback
        print(f"Error in create_video_plan: {e}")
        print(traceback.format_exc())
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video plan: {str(e)}"
        )


@router.get("/templates")
async def get_prompt_templates():
    """Get available prompt templates for video planning."""
    return {
        "templates": list(PROMPT_TEMPLATES.keys()),
        "description": "Pre-defined prompts for different educational contexts"
    }


@router.post("/templates/{template_name}")
async def use_template(template_name: str, request: VideoPlannerRequest):
    """Use a specific template for video planning."""
    if template_name not in PROMPT_TEMPLATES:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{template_name}' not found"
        )

    # Use the specified template
    template_key = template_name
    template = PROMPT_TEMPLATES[template_key]

    # Build additional sections (same as in build_prompt)
    additional_sections = []
    if request.include_activities:
        additional_sections.append("Suggested hands-on activities or experiments")
    if request.include_assessment:
        additional_sections.append("Assessment ideas to check understanding")

    additional_sections_text = "\n".join(f"- {section}" for section in additional_sections) if additional_sections else "No additional sections requested"

    # Format the template based on the template key
    if template_key == "educational_kids":
        prompt = template.format(
            age_group=request.target_audience or "children",
            topic=request.prompt,
            duration=request.video_length or 5,
            learning_objective=request.educational_goal or "educational content",
            additional_sections=additional_sections_text
        )
    elif template_key == "educational_general":
        prompt = template.format(
            topic=request.prompt,
            target_audience=request.target_audience or "general audience",
            video_length=request.video_length or 5,
            educational_goal=request.educational_goal or "educational content",
            additional_sections=additional_sections_text
        )
    else:  # general
        additional_context = ""
        if request.target_audience:
            additional_context += f"Target audience: {request.target_audience}\n"
        if request.video_length:
            additional_context += f"Desired length: {request.video_length} minutes\n"
        if request.educational_goal:
            additional_context += f"Educational goal: {request.educational_goal}\n"
        if request.include_activities:
            additional_context += "Include suggestions for hands-on activities\n"
        if request.include_assessment:
            additional_context += "Include ideas for assessment or knowledge checks\n"

        prompt = template.format(
            topic=request.prompt,
            additional_context=additional_context.strip()
        )

    try:
        llm_service = get_llm_service()
        video_plan = await llm_service.generate_text(
            prompt=prompt,
            max_tokens=1500,
            temperature=0.7
        )

        provider_info = llm_service.get_provider_info()

        return VideoPlannerResponse(
            video_plan=video_plan.strip(),
            prompt_used=prompt,
            model_used=provider_info.get("model", "unknown"),
            tokens_used=None
        )

    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to generate video plan using template: {str(e)}"
        )