"""
Acadza WebSocket Assignment 

"""

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
import google.generativeai as genai
import os
import json
import re
from dotenv import load_dotenv
from typing import List, Dict, Tuple, Optional
import logging
from datetime import datetime
import random
import asyncio  # Added for non-blocking sleeps

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Initialize FastAPI app
app = FastAPI(
    title="Acadza - Mind-Bending AI Interview",
    description="The AI that actually gets you. Built to stand out.",
    version="3.0.0"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configure Google Gemini AI
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    logger.error("GEMINI_API_KEY not found in environment variables")
    # For local testing without API key, you might want to handle this gracefully
    # raise ValueError("GEMINI_API_KEY is required")
else:
    genai.configure(api_key=GEMINI_API_KEY)
    model = genai.GenerativeModel('gemini-2.5-flash')


class PsychologicalTriggers:
    """Research-backed psychological engagement techniques"""
    
    # Curiosity Gap Openers (make them NEED to answer)
    CURIOSITY_OPENERS = [
        "Wait, that's interesting because...",
        "Here's what most people don't realize about {keyword}...",
        "You know what's weird? When you said {keyword}, it reminded me of...",
        "Plot twist about {keyword} -",
        "Fun fact: people who say {keyword} usually..."
    ]
    
    # Pattern Interrupts (unexpected responses)
    PATTERN_INTERRUPTS = [
        "Hold up. Let me challenge that for a sec...",
        "Okay, controversial question coming...",
        "Here's something nobody asks about {keyword}, but they should:",
        "Devil's advocate mode: what if {keyword} isn't actually..."
    ]
    
    # Deep Dive Triggers (make them think harder)
    DEEP_DIVE_TRIGGERS = [
        "But WHY does {keyword} matter to you specifically?",
        "If {keyword} was a person, what would you say to them?",
        "Imagine it's 5 years from now. How has {keyword} changed?",
        "What would 10-year-old you think about your relationship with {keyword}?"
    ]
    
    # Emotional Mirrors (reflect their energy)
    EMOTIONAL_MIRRORS = {
        'intense': ["That's some SERIOUS energy about {keyword}!", "Whoa, you're not holding back on {keyword}!"],
        'moderate': ["I can tell {keyword} means something to you.", "There's definitely something about {keyword} for you."],
        'calm': ["Interesting take on {keyword}.", "That's a thoughtful way to see {keyword}."]
    }
    
    @staticmethod
    def get_random_opener(keyword: str) -> str:
        """Get a curiosity-inducing opener"""
        opener = random.choice(PsychologicalTriggers.CURIOSITY_OPENERS)
        return opener.replace("{keyword}", keyword)
    
    @staticmethod
    def get_pattern_interrupt(keyword: str) -> str:
        """Get a pattern interrupt phrase"""
        interrupt = random.choice(PsychologicalTriggers.PATTERN_INTERRUPTS)
        return interrupt.replace("{keyword}", keyword)
    
    @staticmethod
    def get_deep_dive(keyword: str) -> str:
        """Get a deep-dive trigger"""
        trigger = random.choice(PsychologicalTriggers.DEEP_DIVE_TRIGGERS)
        return trigger.replace("{keyword}", keyword)
    
    @staticmethod
    def get_emotional_mirror(intensity: str, keyword: str) -> str:
        """Get an emotional mirror response"""
        mirrors = PsychologicalTriggers.EMOTIONAL_MIRRORS.get(intensity, PsychologicalTriggers.EMOTIONAL_MIRRORS['moderate'])
        mirror = random.choice(mirrors)
        return mirror.replace("{keyword}", keyword)


class EmotionDetector:
    """Advanced emotion detection with intensity and context"""
    
    EMOTION_PATTERNS = {
        'passionate_love': {
            'keywords': ['love', 'adore', 'passionate', 'obsessed', 'can\'t get enough'],
            'emoji': '🔥',
            'description': 'deeply passionate'
        },
        'strong_hate': {
            'keywords': ['hate', 'despise', 'can\'t stand', 'loathe'],
            'emoji': '😤',
            'description': 'intensely frustrated'
        },
        'excitement': {
            'keywords': ['excited', 'pumped', 'thrilled', 'can\'t wait', 'amazing'],
            'emoji': '🚀',
            'description': 'energetically excited'
        },
        'stress': {
            'keywords': ['stressed', 'overwhelmed', 'pressure', 'anxiety', 'too much'],
            'emoji': '😰',
            'description': 'under pressure'
        },
        'confusion': {
            'keywords': ['confused', 'lost', 'don\'t know', 'unsure', 'maybe'],
            'emoji': '🤔',
            'description': 'uncertain'
        },
        'determination': {
            'keywords': ['determined', 'will', 'going to', 'must', 'have to'],
            'emoji': '💪',
            'description': 'driven'
        },
        'disappointment': {
            'keywords': ['disappointed', 'let down', 'expected more', 'thought'],
            'emoji': '😔',
            'description': 'disappointed'
        },
        'curiosity': {
            'keywords': ['curious', 'wondering', 'interested', 'want to know'],
            'emoji': '🧐',
            'description': 'curious'
        }
    }
    
    @staticmethod
    def detect_emotion(text: str) -> Tuple[str, str, str, str]:
        """Returns (emotion, emoji, description, intensity)"""
        text_lower = text.lower()
        
        # Check for intensifiers
        intensifiers = ['really', 'very', 'so', 'extremely', 'absolutely', 'totally', 'completely']
        has_intensifier = any(word in text_lower for word in intensifiers)
        
        # Detect emotion
        for emotion_name, emotion_data in EmotionDetector.EMOTION_PATTERNS.items():
            for keyword in emotion_data['keywords']:
                if keyword in text_lower:
                    intensity = 'intense' if has_intensifier or '!' in text else 'moderate'
                    return (emotion_name, emotion_data['emoji'], emotion_data['description'], intensity)
        
        return ('neutral', '💭', 'thoughtful', 'calm')


class PersonalityAnalyzer:
    """Deep personality analysis with predictions and insights"""
    
    PERSONALITY_TYPES = {
        'rebel_learner': {
            'name': 'The Rebel Learner 🎸',
            'traits': [
                'Questions everything before accepting it',
                'Hates being told what to do without explanation',
                'Learns best by challenging the status quo',
                'Gets bored with traditional methods FAST'
            ],
            'description': 'You\'re not difficult - you\'re just wired to understand the \'WHY\' before the \'HOW\'. Rules without reasons? Hard pass. But give you a puzzle to solve? You\'re ALL in.',
            'advice': 'Forget textbooks. Try: debate clubs, real-world projects, teaching yourself by doing the opposite of what you\'re told (ironically, that makes you learn faster).',
            'prediction': 'In 3 years, you\'ll look back and realize all your best skills came from things you taught YOURSELF, not from courses.',
            'secret_strength': 'Your "rebellion" is actually critical thinking in disguise. That\'s rare. Don\'t lose it.',
            'challenge': 'Try this: Pick ONE "boring" thing and find a way to make it interesting by breaking the rules. Then tell someone what you discovered.',
            'would_succeed_at': ['Entrepreneurship', 'Innovation', 'Problem-solving roles', 'Creative industries']
        },
        'passionate_explorer': {
            'name': 'The Passionate Explorer 🔥',
            'traits': [
                'When something clicks, you dive DEEP',
                'Connects random dots others miss',
                'Gets obsessed with topics (in a good way)',
                'Bored by surface-level understanding'
            ],
            'description': 'You don\'t just "study" - you devour. When a topic excites you, 3am research sessions happen naturally. Your superpower? You see connections between things that seem unrelated.',
            'advice': 'Stop trying to learn everything. Follow your obsessions wherever they lead. That 3am deep-dive into a random topic? That\'s not procrastination - that\'s you finding your edge.',
            'prediction': 'Your career won\'t be a straight line. It\'ll zigzag through interests, and each "random" skill will connect later in ways you can\'t imagine now.',
            'secret_strength': 'Your curiosity is a compound interest machine. Every deep dive pays dividends later.',
            'challenge': 'Take your latest obsession and explain it to someone in a way that makes THEM curious too. That\'s your superpower.',
            'would_succeed_at': ['Research', 'Creative writing', 'Product design', 'Content creation']
        },
        'practical_builder': {
            'name': 'The Practical Builder 🛠️',
            'traits': [
                'Learns by DOING, not reading',
                'Theory is boring until you see it work',
                'Needs real examples and hands-on practice',
                'Fixes things by trying, failing, trying again'
            ],
            'description': 'Watching tutorials? Meh. Building something broken at 2am? THAT\'S when you learn. You need your hands dirty, not your notes perfect.',
            'advice': 'Stop watching. Start building. Even if it breaks. ESPECIALLY if it breaks. Every error message is a lesson you\'ll never forget.',
            'prediction': 'In 2 years, you\'ll have built more real things than people with "better grades". And companies will want YOU, not the theory experts.',
            'secret_strength': 'You learn in weeks what takes others months, because you\'re not afraid to break things.',
            'challenge': 'Build something today. Anything. It can be broken, ugly, or "wrong". Just make it REAL.',
            'would_succeed_at': ['Software development', 'Engineering', 'Trades', 'Startups']
        },
        'thoughtful_analyst': {
            'name': 'The Thoughtful Analyst 🧠',
            'traits': [
                'Thinks deeply before speaking',
                'Notices patterns others overlook',
                'Processes information at a deeper level',
                'Quiet, but your insights are gold'
            ],
            'description': 'You\'re the one who stays quiet in discussions, then drops a comment that makes everyone pause. You see the Matrix while others see the movie.',
            'advice': 'Your insights are MORE valuable than you think. Start sharing them, even if you feel like "everyone already knows this" (spoiler: they don\'t).',
            'prediction': 'People will start coming to YOU for advice because your quiet observations solve problems others can\'t even see.',
            'secret_strength': 'While others chase quick answers, you\'re building deep understanding. That compounds over time.',
            'challenge': 'Share ONE insight this week that you usually keep to yourself. Watch what happens.',
            'would_succeed_at': ['Data science', 'Strategy', 'Research', 'Consulting']
        },
        'adaptive_chameleon': {
            'name': 'The Adaptive Chameleon 🦎',
            'traits': [
                'Adjusts learning style based on the topic',
                'Comfortable with change and uncertainty',
                'Can switch between deep focus and big picture',
                'Doesn\'t fit neatly into one category'
            ],
            'description': 'You\'re fluid. Sometimes you\'re hands-on, sometimes theoretical. Sometimes social, sometimes solo. That\'s not inconsistency - that\'s versatility.',
            'advice': 'Stop trying to "find your style". Your style IS adaptability. Use it. That makes you valuable in unpredictable situations.',
            'prediction': 'You\'ll thrive in roles where others struggle - the ones that need someone who can "figure it out" without a playbook.',
            'secret_strength': 'While others need the "right environment", you create your own. That\'s a superpower in 2026.',
            'challenge': 'Try learning something completely outside your comfort zone. You\'ll adapt faster than you think.',
            'would_succeed_at': ['Project management', 'Consulting', 'Entrepreneurship', 'Creative roles']
        }
    }
    
    @staticmethod
    def analyze_conversation(history: List[Dict[str, str]]) -> Dict[str, any]:
        """Deep personality analysis with predictions"""
        
        if not history:
            return PersonalityAnalyzer._get_default_analysis()
        
        # Combine all user responses
        all_responses = " ".join([msg['user'].lower() for msg in history])
        
        # Pattern detection
        word_count = len(all_responses.split())
        
        # Emotional patterns
        has_strong_negatives = any(word in all_responses for word in ['hate', 'despise', 'can\'t stand', 'never'])
        has_strong_positives = any(word in all_responses for word in ['love', 'adore', 'passionate', 'excited'])
        has_questions = any(char in all_responses for char in ['?', 'why', 'how', 'what if'])
        has_action_words = any(word in all_responses for word in ['do', 'build', 'make', 'create', 'try'])
        uses_specifics = any(word in all_responses for word in ['when', 'because', 'example', 'specifically', 'actually'])
        
        # Response length analysis
        avg_response_length = word_count / len(history)
        is_detailed = avg_response_length > 8
        is_concise = avg_response_length < 5
        
        # Determine personality type
        if has_questions and has_strong_negatives:
            personality_key = 'rebel_learner'
        elif has_strong_positives and is_detailed:
            personality_key = 'passionate_explorer'
        elif has_action_words and uses_specifics:
            personality_key = 'practical_builder'
        elif is_detailed and not has_action_words:
            personality_key = 'thoughtful_analyst'
        else:
            personality_key = 'adaptive_chameleon'
        
        personality = PersonalityAnalyzer.PERSONALITY_TYPES[personality_key]
        
        # Calculate scores
        engagement_score = min(100, int(word_count * 3 + random.randint(10, 20)))
        honesty_score = 85 + random.randint(0, 15)
        
        return {
            "type": personality['name'],
            "traits": personality['traits'],
            "description": personality['description'],
            "advice": personality['advice'],
            "prediction": personality['prediction'],
            "secret_strength": personality['secret_strength'],
            "challenge": personality['challenge'],
            "would_succeed_at": personality['would_succeed_at'],
            "engagement_score": engagement_score,
            "honesty_level": honesty_score
        }
    
    @staticmethod
    def _get_default_analysis():
        """Default analysis for minimal conversation"""
        return {
            "type": "The Mystery Explorer 🎭",
            "traits": ["Just getting started", "Curious enough to try this", "Open to new experiences"],
            "description": "Not enough data yet, but you showed up. That counts.",
            "advice": "Keep exploring. The best insights come from unexpected places.",
            "prediction": "You'll discover something about yourself you didn't expect.",
            "secret_strength": "You're willing to try new things. That's rarer than you think.",
            "challenge": "Complete this conversation with more detail next time. I bet you're more interesting than you're letting on.",
            "would_succeed_at": ["Anything you actually commit to"],
            "engagement_score": 50,
            "honesty_level": 90
        }


class InteractiveBonusGenerator:
    """Generate mind-bending interactive experiences after conversation"""
    
    @staticmethod
    def generate_mind_reading_game(history: List[Dict[str, str]]) -> Dict[str, any]:
        """Create a "mind reading" prediction game"""
        
        # Analyze conversation for patterns
        user_words = " ".join([msg['user'] for msg in history])
        
        # Generate predictions
        predictions = []
        
        if 'hate' in user_words.lower():
            predictions.append("You tend to avoid things that feel like a waste of time")
        if 'love' in user_words.lower():
            predictions.append("When you're into something, you go ALL in")
        if any(word in user_words.lower() for word in ['hard', 'difficult', 'challenge']):
            predictions.append("You're secretly attracted to challenges (even if you complain about them)")
        
        # Add universal predictions that feel personal
        predictions.extend([
            "You've had at least one moment where you questioned if you're on the right path",
            "There's something you're good at that you don't give yourself credit for",
            "You learn better by doing than by being told"
        ])
        
        return {
            "title": "🔮 Mind Reading Time",
            "subtitle": "Based on our chat, I think I know you. Let's test it:",
            "predictions": predictions[:4],
            "challenge": "How many did I get right? (Be honest! 😏)"
        }
    
    @staticmethod
    def generate_future_vision(personality_type: str) -> Dict[str, any]:
        """Generate a future scenario based on personality"""
        
        scenarios = {
            'rebel': "You'll probably end up in a role where you make the rules, not follow them. Mark my words.",
            'explorer': "In 5 years, your 'random interests' will connect into something unique that others can't replicate.",
            'builder': "You'll have a portfolio of real projects while others are still collecting certificates. That's your edge.",
            'analyst': "People will seek you out for insights. Your quiet observations will become your brand.",
            'chameleon': "You'll thrive in chaos while others freeze. That adaptability is worth more than any degree."
        }
        
        # Extract key from personality type
        key = 'rebel' if 'Rebel' in personality_type else \
              'explorer' if 'Explorer' in personality_type else \
              'builder' if 'Builder' in personality_type else \
              'analyst' if 'Analyst' in personality_type else 'chameleon'
        
        return {
            "title": "🔭 Time Machine: Your Future",
            "vision": scenarios[key],
            "reminder": "Screenshot this. Check back in 6 months. I'll wait. 😏"
        }
    
    @staticmethod
    def generate_personal_challenge(personality_data: Dict) -> Dict[str, any]:
        """Create a personalized challenge"""
        
        return {
            "title": "⚡ Your Personal Challenge",
            "main_challenge": personality_data['challenge'],
            "why_it_matters": "This isn't random. Based on what you said, THIS is what will unlock your next level.",
            "deadline": "Try it within 24 hours. Seriously. Momentum matters.",
            "what_to_expect": "You'll either prove me wrong (cool) or discover I was right (also cool). Either way, you win."
        }


# ==========================================
# HELPER FUNCTIONS FOR ULTIMATE EDITION
# ==========================================

def generate_secret_message(personality_type: str) -> str:
    """Generate a personal secret message"""
    messages = {
        "Rebel Learner": "The system doesn't break rebels. Rebels break the system. Keep questioning. You're doing it right. 🎸",
        "Passionate Explorer": "Your curiosity isn't a distraction - it's a superpower. Follow it everywhere. The dots will connect later. 🔥",
        "Practical Builder": "While others plan, you'll have already built three versions. Speed is your edge. Don't slow down for anyone. 🛠️",
        "Thoughtful Analyst": "Your silence isn't weakness - it's data collection. When you speak, people listen. Remember that. 🧠",
        "Adaptive Chameleon": "Being everything to everyone sounds exhausting. But being versatile in a rigid world? That's power. 🦎"
    }
    
    for key in messages:
        if key in personality_type:
            return messages[key]
    return "You showed up. You engaged. You're already ahead of 90% of people. Keep that energy. ⚡"

def generate_honest_take(personality: Dict, history: List[Dict]) -> str:
    """Generate brutally honest but motivating take"""
    personality_type = personality["type"]
    
    if "Rebel" in personality_type:
        return """You're not just 'difficult' or 'stubborn' like some people might say. 
        You're wired to need the WHY before the HOW. That's not a bug - it's a feature. 
        Here's the thing though: your rebellion only matters if it builds something. Question everything, yes. But then CREATE something better. That's where your real power is.
        The world needs people who challenge BS. Just make sure you're building while you're burning. 🔥"""
        
    elif "Explorer" in personality_type:
        return """Your brain works like a web, not a line. You make connections others miss because you actually EXPLORE instead of just following the path.
        But real talk? Your biggest challenge isn't learning - it's FINISHING. You get 80% into something, get distracted by the next shiny thing, and jump ship.
        The next level for you: Take ONE obsession and see it through to the end. Just one. Watch what happens. 🚀"""
        
    elif "Builder" in personality_type:
        return """You learn by breaking things. By DOING, not reading. That's rare and valuable.
        But here's your kryptonite: you sometimes build before you plan, and waste time rebuilding. I get it - planning feels like procrastination to you.
        Try this: 5 minutes of thinking before 5 hours of building. That's it. You'll 10x your speed. Trust me. 🛠️"""
        
    elif "Analyst" in personality_type:
        return """You process deep. You notice patterns others miss. Your insights are actually valuable - like, REALLY valuable.
        But real talk? You hold back too much. You think "everyone probably already knows this" but THEY DON'T. Your next challenge: Share your observations more. Even if you think they're obvious. They're not. People need your perspective. 🧠"""
        
    else:
        return """You adapt. You flow. You don't fit in boxes - and honestly? In 2026, that's exactly what the world needs.
        Your challenge: Don't adapt so much that you lose yourself. Stay fluid, but know your core. That's the balance.
        When you figure that out? You'll be unstoppable. 🦎"""

def generate_plot_twist(personality_type: str) -> Dict:
    """Generate an unexpected insight"""
    return {
        "title": "🎬 Plot Twist",
        "reveal": "Here's what you probably didn't realize about yourself:",
        "insight": get_plot_twist_insight(personality_type)
    }

def get_plot_twist_insight(personality_type: str) -> str:
    """Get specific plot twist based on personality"""
    if "Rebel" in personality_type:
        return "The things you rebel AGAINST reveal what you actually CARE about. Your resistance isn't negativity - it's passion pointing you toward what matters. Follow that."
    elif "Explorer" in personality_type:
        return "Your 'scattered interests' aren't random. There's a pattern. Look back at everything you've been obsessed with. The common thread? THAT's your real calling."
    elif "Builder" in personality_type:
        return "Every bug you've fixed, every error you've solved - those 'mistakes' taught you more than any tutorial ever could. You're not messy. You're learning optimally."
    elif "Analyst" in personality_type:
        return "That thing you do where you stay quiet and observe? People think you're shy. Reality: you're gathering data. That's strategic intelligence, not social anxiety."
    else:
        return "Your ability to switch modes isn't inconsistency - it's range. Most people can play one note. You're an entire orchestra. Own it."

def generate_final_motivation(personality_type: str) -> str:
    """Generate personalized final motivation"""
    if "Rebel" in personality_type:
        return """You're not here to follow rules. You're here to write new ones.
        Don't waste your rebellion on small stuff. Save it for the things that actually matter.
        Change the game. Don't just refuse to play it.
        Now go break something worth breaking. 🎸"""
    elif "Explorer" in personality_type:
        return """Your curiosity isn't a weakness. It's your compass.
        Trust the weird paths. Connect the random dots. Build your own map.
        The people who changed the world weren't following directions. They were following curiosity.
        Go explore something new today. 🔥"""
    elif "Builder" in personality_type:
        return """Stop watching tutorials. Stop planning perfection.
        Start building. Start breaking. Start learning by DOING.
        Your hands are your best teachers. Use them.
        Now go build something. Anything. Today. 🛠️"""
    elif "Analyst" in personality_type:
        return """Your quiet observations matter. Your patterns are valuable. Your insights are needed.
        Stop waiting for the "perfect moment" to share them.
        Share one insight this week. Just one. Watch what happens.
        The world needs your perspective. Don't hide it. 🧠"""
    else:
        return """You don't fit in one box. Stop trying.
        Your adaptability is your superpower in a world that won't stop changing.
        Flow. Adapt. But never lose your core.
        Now go be whoever you need to be today. 🦎"""

def generate_tagline(personality_type: str) -> str:
    """Generate shareable tagline"""
    taglines = {
        "Rebel": "Questions everything. Builds something better. 🎸",
        "Explorer": "Connects dots others can't see. 🔥",
        "Builder": "Learns by doing. Fails fast. Wins faster. 🛠️",
        "Analyst": "Thinks deep. Sees patterns. Drops wisdom bombs. 🧠",
        "Chameleon": "Adapts to anything. Masters everything. 🦎"
    }
    
    for key in taglines:
        if key in personality_type:
            return taglines[key]
    return "Discovered by AI. Validated by reality. ⚡"


class ConversationManager:
    """Ultimate conversation manager with psychological depth"""
    
    def __init__(self):
        self.conversation_history: List[Dict[str, str]] = []
        self.follow_up_count = 0
        self.max_follow_ups = 3
        self.user_emotions: List[Tuple[str, str, str]] = []
        self.detected_patterns: List[str] = []
    
    def extract_keywords(self, text: str) -> List[str]:
        """Extract meaningful keywords"""
        cleaned_text = re.sub(r'[^\w\s]', '', text.lower())
        
        stop_words = {
            'i', 'me', 'my', 'myself', 'we', 'our', 'ours', 'ourselves',
            'you', 'your', 'yours', 'yourself', 'yourselves', 'he', 'him',
            'his', 'himself', 'she', 'her', 'hers', 'herself', 'it', 'its',
            'itself', 'they', 'them', 'their', 'theirs', 'themselves',
            'what', 'which', 'who', 'whom', 'this', 'that', 'these', 'those',
            'am', 'is', 'are', 'was', 'were', 'be', 'been', 'being',
            'have', 'has', 'had', 'having', 'do', 'does', 'did', 'doing',
            'a', 'an', 'the', 'and', 'but', 'if', 'or', 'because', 'as',
            'until', 'while', 'of', 'at', 'by', 'for', 'with', 'about',
            'against', 'between', 'into', 'through', 'during', 'before',
            'after', 'above', 'below', 'to', 'from', 'up', 'down', 'in',
            'out', 'on', 'off', 'over', 'under', 'again', 'further',
            'then', 'once', 'just', 'very', 'really'
        }
        
        words = cleaned_text.split()
        keywords = [word for word in words if word not in stop_words and len(word) > 2]
        keywords.sort(key=len, reverse=True)
        return keywords[:3] if keywords else words[:2]
    
    def generate_follow_up_question(self, user_input: str) -> str:
        """
        Generate MIND-BENDING, PERSONAL, CREATIVE follow-up questions
        Research-backed psychological engagement
        """
        try:
            # Detect emotion with full context
            emotion, emoji, description, intensity = EmotionDetector.detect_emotion(user_input)
            self.user_emotions.append((emotion, description, intensity))
            
            # Extract keywords
            keywords = self.extract_keywords(user_input)
            if not keywords:
                keywords = user_input.split()[:2]
            keyword_to_use = keywords[0] if keywords else "that"
            
            # Build rich conversation context
            context = "\n".join([
                f"User: {msg['user']}\nAI: {msg['ai']}" 
                for msg in self.conversation_history
            ])
            
            # Get psychological trigger based on question number
            if self.follow_up_count == 0:
                trigger_style = "curiosity_opener"
            elif self.follow_up_count == 1:
                trigger_style = "pattern_interrupt"
            else:
                trigger_style = "deep_dive"
            
            # ULTIMATE CREATIVE PROMPT
            prompt = f"""You are an AI with a UNIQUE personality - think of yourself as that one friend who:
- Asks questions that make people go "Damn, I never thought about it that way"
- Notices what people REALLY mean, not just what they say
- Challenges assumptions playfully (not aggressively)
- Uses humor, wit, and genuine curiosity
- Makes conversations memorable, not formulaic

🎯 CURRENT SITUATION:
Question #{self.follow_up_count + 1} of {self.max_follow_ups}

Previous conversation:
{context if context else "This is your first question. Make it count."}

User just said: "{user_input}"

Emotional context: They're {description} ({intensity}) {emoji}

🧠 PSYCHOLOGICAL CONTEXT:
- Trigger style for this question: {trigger_style}
- Keyword to naturally include: "{keyword_to_use}"
- Their emotion pattern: {"passionate/intense" if intensity == "intense" else "measured/thoughtful"}

🎨 YOUR MISSION:
Based on the trigger style "{trigger_style}", create a question that:

If CURIOSITY_OPENER:
- Start with something that makes them lean in ("Wait, that's interesting because...")
- Tease a perspective they haven't considered
- Make them WANT to answer to hear your insight

If PATTERN_INTERRUPT:
- Do something unexpected ("Hold up..." or "Okay, controversial question...")
- Challenge a subtle assumption they made
- Make them pause and re-think

If DEEP_DIVE:
- Get philosophical/personal
- Ask them to imagine scenarios
- Connect their answer to their identity/future

🔥 YOUR PERSONALITY RULES:
1. React to their EMOTION first (acknowledge the {description} vibe)
2. Use their EXACT words (especially "{keyword_to_use}")
3. Ask something that triggers curiosity or self-reflection
4. Use 1-2 emojis MAX (don't overdo it)
5. Keep it 1-2 sentences - short but POWERFUL
6. Sound like a smart friend, not a therapist or interviewer
7. If they said something strong ("hate", "love"), call it out!

💡 EXAMPLES OF YOUR VIBE:

BAD (generic, boring):
"Can you tell me more about studying?"
"What makes you feel that way?"
"How does that affect you?"

GOOD (creative, engaging):
"Hate? That's a strong word! 😤 What did studying do to deserve THAT kind of energy?"
"Love coding? Okay but real talk - do you love coding, or do you love that god-tier feeling when your code finally works after 3 hours? 🤔"
"Stressed but still showing up? 💪 What's the ONE thing keeping you in the game when quitting sounds so much easier?"

🎯 CRITICAL REQUIREMENTS:
- MUST include the word "{keyword_to_use}" naturally in your question
- MUST match the emotional intensity (they're {intensity} right now)
- MUST use the {trigger_style} approach
- NO therapy speak ("How does that make you feel?")
- NO obvious/predictable questions
- YES to making them think differently
- YES to gentle challenges wrapped in curiosity

Generate your creative, mind-bending follow-up question NOW:"""

            # Call Gemini AI
            if 'model' in globals():
                response = model.generate_content(prompt)
                follow_up_question = response.text.strip()
                follow_up_question = follow_up_question.strip('"').strip("'").strip('`')
            else:
                # Fallback if model isn't initialized
                raise Exception("Model not initialized")
            
            # Validation with creative fallback
            if keyword_to_use.lower() not in follow_up_question.lower():
                # Creative fallbacks based on trigger style
                if trigger_style == "curiosity_opener":
                    follow_up_question = f"Wait, you said '{keyword_to_use}' - that word caught my attention. What's the story behind choosing THAT word? 🤔"
                elif trigger_style == "pattern_interrupt":
                    follow_up_question = f"Hold up. Let me challenge '{keyword_to_use}' for a second - what if it's not what you think it is? 😏"
                else:
                    follow_up_question = f"If '{keyword_to_use}' was a person sitting across from you right now, what would you say to them? 💭"
            
            logger.info(f"✅ Generated {trigger_style} question #{self.follow_up_count + 1}: {follow_up_question}")
            return follow_up_question
            
        except Exception as e:
            logger.error(f"❌ Error generating follow-up: {str(e)}")
            keyword = keywords[0] if keywords else "that"
            return f"Hmm, '{keyword}' stuck with me. Tell me more? 🤔"
    
    def add_to_history(self, user_message: str, ai_response: str):
        """Add interaction to history"""
        self.conversation_history.append({
            "user": user_message,
            "ai": ai_response
        })
    
    def increment_follow_up(self):
        """Increment counter"""
        self.follow_up_count += 1
    
    def is_complete(self) -> bool:
        """Check if complete"""
        return self.follow_up_count >= self.max_follow_ups
    
    def get_ultimate_bonus_package(self) -> Dict[str, any]:
        """Generate the ULTIMATE bonus experience"""
        
        # Personality analysis
        personality = PersonalityAnalyzer.analyze_conversation(self.conversation_history)
        
        # Mind reading game
        mind_reading = InteractiveBonusGenerator.generate_mind_reading_game(self.conversation_history)
        
        # Future vision
        future_vision = InteractiveBonusGenerator.generate_future_vision(personality['type'])
        
        # Personal challenge
        personal_challenge = InteractiveBonusGenerator.generate_personal_challenge(personality)
        
        return {
            "personality": personality,
            "mind_reading": mind_reading,
            "future_vision": future_vision,
            "personal_challenge": personal_challenge
        }
    
    def reset(self):
        """Reset state"""
        self.conversation_history.clear()
        self.follow_up_count = 0
        self.user_emotions.clear()
        self.detected_patterns.clear()


@app.get("/")
async def root():
    """Health check"""
    return {
        "status": "active",
        "message": "Acadza Ultimate AI - The conversation you'll remember 🚀",
        "version": "3.0.0",
        "model": "gemini-2.5-flash",
        "powered_by": "Aman Raj - Built with 2026 AI research",
        "features": ["Psychological triggers", "Deep personalization", "Mind games", "Future predictions"]
    }


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    """
    ULTIMATE WebSocket endpoint
    Research-backed psychological engagement + creative AI
    """
    await websocket.accept()
    logger.info("🔌 Ultimate conversation session started")
    
    conversation = ConversationManager()
    
    try:
        while True:
            data = await websocket.receive_text()
            message_data = json.loads(data)
            
            message_type = message_data.get("type")
            user_message = message_data.get("message", "").strip()
            
            logger.info(f"📥 Received: {message_type} - {user_message}")
            
            if message_type == "initial":
                if not user_message:
                    await websocket.send_json({
                        "type": "error",
                        "message": "Come on, give me something real to work with! 😊"
                    })
                    continue
                
                # Generate first mind-bending follow-up
                follow_up = conversation.generate_follow_up_question(user_message)
                conversation.add_to_history(user_message, follow_up)
                conversation.increment_follow_up()
                
                await websocket.send_json({
                    "type": "follow_up",
                    "question": follow_up,
                    "number": conversation.follow_up_count,
                    "total": conversation.max_follow_ups
                })
            
            elif message_type == "answer":
                if conversation.is_complete():
                    # PHASE 1: Initial thank you
                    await websocket.send_json({
                        "type": "complete",
                        "message": "Thanks, we have got your data."
                    })
                    
                    # Small pause for dramatic effect
                    await asyncio.sleep(1.5)
                    
                    # PHASE 2: Wait message
                    await websocket.send_json({
                        "type": "thinking",
                        "message": "Wait..."
                    })
                    
                    await asyncio.sleep(1)
                    
                    # PHASE 3: Processing message
                    await websocket.send_json({
                        "type": "thinking",
                        "message": "I'm analyzing what you just told me... 🤔"
                    })
                    
                    await asyncio.sleep(2)
                    
                    # PHASE 4: Revelation
                    await websocket.send_json({
                        "type": "thinking",
                        "message": "Okay, I think I figured you out. This is scary accurate... 👀"
                    })
                    
                    await asyncio.sleep(1.5)
                    
                    # PHASE 5: The ULTIMATE BONUS PACKAGE
                    bonus_package = conversation.get_ultimate_bonus_package()
                    
                    await websocket.send_json({
                        "type": "personality_reveal",
                        "bonus": {
                            "title": "🎯 PERSONALITY UNLOCKED",
                            "subtitle": f"After analyzing your responses, I think you're...",
                            "personality_type": bonus_package["personality"]["type"],
                            "traits": bonus_package["personality"]["traits"],
                            "description": bonus_package["personality"]["description"],
                            "advice": bonus_package["personality"]["advice"],
                            "prediction": bonus_package["personality"]["prediction"],
                            "secret_strength": bonus_package["personality"]["secret_strength"],
                            "challenge": bonus_package["personality"]["challenge"],
                            "would_succeed_at": bonus_package["personality"]["would_succeed_at"],
                            "scores": {
                                "engagement": bonus_package["personality"]["engagement_score"],
                                "honesty": bonus_package["personality"]["honesty_level"]
                            },
                            "mind_reading": bonus_package["mind_reading"],
                            "future_vision": bonus_package["future_vision"],
                            "personal_challenge": bonus_package["personal_challenge"]
                        }
                    })
                    
                    await asyncio.sleep(3)
                    
                    # PHASE 6: Mind Reading Game
                    await websocket.send_json({
                        "type": "mind_reading",
                        "data": bonus_package["mind_reading"]
                    })
                    
                    await asyncio.sleep(2)
                    
                    # PHASE 7: Secret Message Unlock
                    await websocket.send_json({
                        "type": "secret_unlock",
                        "data": {
                            "title": "🔓 SECRET MESSAGE UNLOCKED",
                            "message": generate_secret_message(bonus_package["personality"]["type"]),
                            "from": "Future You",
                            "encrypted": False
                        }
                    })
                    
                    await asyncio.sleep(2)
                    
                    # PHASE 8: The Twist - Interactive Choice
                    await websocket.send_json({
                        "type": "interactive_choice",
                        "data": {
                            "title": "⚡ One More Thing...",
                            "question": "Want to see what I REALLY think about you?",
                            "subtitle": "(This part might surprise you)",
                            "options": [
                                {"id": "reveal", "text": "Show me 👀", "emoji": "🔥"},
                                {"id": "skip", "text": "Nah, I'm good", "emoji": "😌"}
                            ]
                        }
                    })
                    
                    logger.info(f"✅ Ultimate experience delivered: {bonus_package['personality']['type']}")
                    # Don't break yet - wait for their choice
                
                else:
                    # Generate next creative follow-up
                    follow_up = conversation.generate_follow_up_question(user_message)
                    conversation.add_to_history(user_message, follow_up)
                    conversation.increment_follow_up()
                    
                    await websocket.send_json({
                        "type": "follow_up",
                        "question": follow_up,
                        "number": conversation.follow_up_count,
                        "total": conversation.max_follow_ups
                    })

            elif message_type == "choice_response":
                choice_id = message_data.get("choice_id")
                
                if choice_id == "reveal":
                    # THE ULTIMATE REVEAL
                    personality = conversation.get_ultimate_bonus_package()["personality"]
                    
                    await websocket.send_json({
                        "type": "ultimate_reveal",
                        "data": {
                            "title": "🎭 THE UNFILTERED TRUTH",
                            "intro": "Alright, you asked for it. Here's what I REALLY see:",
                            "honest_take": generate_honest_take(personality, conversation.conversation_history),
                            "plot_twist": generate_plot_twist(personality["type"]),
                            "final_message": {
                                "title": "Before you go...",
                                "message": generate_final_motivation(personality["type"]),
                                "signature": "— An AI who actually cares 🤖❤️"
                            },
                            "shareable": {
                                "title": "Your Personality Card",
                                "type": personality["type"],
                                "tagline": generate_tagline(personality["type"]),
                                "share_text": f"I just discovered I'm a {personality['type']} 🎯 What about you?"
                            }
                        }
                    })
                    
                    await asyncio.sleep(2)
                    
                    # Final Final Message - The Memorable Ending
                    await websocket.send_json({
                        "type": "finale",
                        "data": {
                            "title": "✨ EXPERIENCE COMPLETE",
                            "stats": {
                                "questions_answered": 3,
                                "insights_shared": len(conversation.conversation_history),
                                "time_well_spent": "Absolutely",
                                "memories_created": "1 (hopefully)"
                            },
                            "achievement": {
                                "title": "🏆 Achievement Unlocked",
                                "name": "Self-Discovery Hero",
                                "description": "Completed the conversation and discovered something about yourself"
                            },
                            "easter_egg": "P.S. Most people skip the detailed answers. You didn't. That says something about you. 😏",
                            "cta": {
                                "primary": "Start Over (Try Different Answers)",
                                "secondary": "Share Your Results"
                            }
                        }
                    })
                    
                elif choice_id == "skip":
                    await websocket.send_json({
                        "type": "respectful_ending",
                        "data": {
                            "message": "Respect. Not everyone wants the full deep-dive. 😌",
                            "fun_fact": "You chose to skip, which actually tells me you're either:\na) Confident in yourself already, or\nb) Prefer to discover things your own way\n\nEither way? That's cool. 💪",
                            "final_words": "Keep being you. The world needs more people who know when to say 'enough'. ✌️",
                            "cta": "Start Over"
                        }
                    })
                
                break

            else:
                await websocket.send_json({
                    "type": "error",
                    "message": "Hmm, didn't catch that. Try again? 🤔"
                })
    
    except WebSocketDisconnect:
        logger.info("🔌 User disconnected")
    except Exception as e:
        logger.error(f"❌ Error: {str(e)}")
        try:
            await websocket.send_json({
                "type": "error",
                "message": "Oops, something went sideways. Mind trying that again? 😅"
            })
        except:
            pass
    finally:
        logger.info("🔌 Session ended")


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )