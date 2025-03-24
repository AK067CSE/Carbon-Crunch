import os
from dotenv import load_dotenv
import google.generativeai as genai
from typing import Dict, List
import ast
import re
from collections import defaultdict

class AiCodeReviewer:
    def __init__(self):
        load_dotenv()
        self.key = os.getenv("GOOGLE_API_KEY")
        genai.configure(api_key=self.key)
        self.model = genai.GenerativeModel(model_name="gemini-1.5-flash")
        self.categories = {
            "naming": 10,
            "modularity": 20,
            "comments": 20,
            "formatting": 15,
            "reusability": 15,
            "best_practices": 20
        }

    def analyze_code(self, code: str, language: str, context: str = None) -> Dict:
        # Map file extensions to language names
        language_map = {
            "py": "python",
            "js": "javascript",
            "jsx": "javascript"
        }
        
        # Convert file extension to language name
        language = language_map.get(language, language)

        if language == "python":
            static_analysis = self._analyze_python(code)
        elif language in ["javascript", "jsx"]:
            static_analysis = self._analyze_javascript(code)
        else:
            raise ValueError(f"Unsupported language: {language}")

        ai_analysis = self._get_ai_analysis(code, language, context)
        combined_metrics = self._combine_metrics(static_analysis, ai_analysis["scores"])
        recommendations = self._combine_recommendations(static_analysis, ai_analysis["recommendations"])
        return {
            "overall_score": self._calculate_overall_score(combined_metrics),
            "breakdown": combined_metrics,
            "recommendations": recommendations[:5],
            "detailed_feedback": ai_analysis["detailed_feedback"]
        }

    def _get_ai_analysis(self, code: str, language: str, context: str) -> Dict:
        prompt = f"""
        You are an expert in {language} code review. Analyze the provided code for:
        1. Code Structure and Organization
        2. Naming Conventions
        3. Error Handling
        4. Performance Optimization
        5. Security Practices
        6. Documentation and Comments
        7. Best Practices
         
        Provide:
        - Detailed feedback with examples
        - Specific recommendations
        - Score each category out of 100
        - Provide at least 3 recommendations for improvement
        
        Code to review:
        ```{language}
        {code}
        ```
        
        Context: {context if context else 'No specific context provided'}
        """
        response = self.model.generate_content(prompt)
        text_response = response.text
        return {
            "detailed_feedback": text_response,
            "recommendations": self._extract_recommendations(text_response),
            "scores": self._extract_scores(text_response)
        }

    def _extract_scores(self, feedback: str) -> Dict:
        scores = {}
        for line in feedback.split('\n'):
            match = re.match(r"(\w+):\s*(\d+)", line)
            if match:
                scores[match.group(1).lower()] = int(match.group(2))
        return scores

    def _extract_recommendations(self, feedback: str) -> List[str]:
        return [line[2:] for line in feedback.split("\n") if line.startswith("- ")]

    def _analyze_python(self, code: str) -> Dict:
        try:
            tree = ast.parse(code)
        except SyntaxError:
            return {category: 0 for category in self.categories}

        return {
            "naming": self._check_naming_conventions(tree),
            "modularity": self._check_modularity(tree),
            "comments": self._check_comments(code),
            "formatting": self._check_formatting(code),
            "reusability": self._check_reusability(tree),
            "best_practices": self._check_best_practices(tree)
        }

    def _check_naming_conventions(self, tree: ast.AST) -> int:
        score = 10
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef, ast.Name)):
                if not re.match(r'^[a-z][a-z0-9_]*$', node.name if hasattr(node, 'name') else node.id):
                    score -= 2
        return max(0, score)

    def _check_modularity(self, tree: ast.AST) -> int:
        score = 20
        for node in ast.walk(tree):
            if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
                if len(node.body) > 20:
                    score -= 5
                if len(node.args.args) > 5:
                    score -= 3
        return max(0, score)

    def _check_comments(self, code: str) -> int:
        score = 20
        docstrings = sum(1 for node in ast.walk(ast.parse(code)) if isinstance(node, ast.Expr) and isinstance(node.value, ast.Str))
        return min(20, score + docstrings * 5)

    def _check_formatting(self, code: str) -> int:
        score = 15
        for line in code.split('\n'):
            if len(line) > 79 or (line.strip() and not line.startswith(' ' * 4)):
                score -= 2
        return max(0, score)

    def _check_reusability(self, tree: ast.AST) -> int:
        score = 15
        function_calls = defaultdict(int)
        for node in ast.walk(tree):
            if isinstance(node, ast.Call) and hasattr(node.func, 'id'):
                function_calls[node.func.id] += 1
        return max(0, score - sum(2 for count in function_calls.values() if count > 3))

    def _check_best_practices(self, tree: ast.AST) -> int:
        score = 20
        for node in ast.walk(tree):
            if isinstance(node, ast.Global):
                score -= 5
            elif isinstance(node, ast.Try) and not any(isinstance(h, ast.ExceptHandler) for h in node.handlers):
                score -= 3
        return max(0, score)

    def _combine_metrics(self, static_metrics: Dict, ai_metrics: Dict) -> Dict:
        return {
            category: round((static_metrics.get(category, 0) * 0.7 + ai_metrics.get(category, 0) * 0.3) * (weight / 100))
            for category, weight in self.categories.items()
        }

    def _combine_recommendations(self, static_metrics: Dict, ai_recommendations: List[str]) -> List[str]:
        static_recommendations = []
        if static_metrics["naming"] < 8:
            static_recommendations.append("Use snake_case for function and variable names.")
        if static_metrics["modularity"] < 15:
            static_recommendations.append("Consider breaking down long functions into smaller, focused functions.")
        return list(set(static_recommendations + ai_recommendations))[:5]

    def _calculate_overall_score(self, metrics: Dict[str, int]) -> int:
        return round((sum(metrics.values()) / sum(self.categories.values())) * 100)
