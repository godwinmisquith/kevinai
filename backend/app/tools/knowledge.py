"""Knowledge tool for storing and retrieving organizational knowledge."""

from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any, Dict, List, Optional
import uuid

from app.tools.base import BaseTool


class KnowledgeScope(str, Enum):
    """Scope of knowledge application."""
    
    NO_REPOS = "no_repos"
    SPECIFIC_REPOS = "specific_repos"
    ALL_REPOS = "all_repos"


class KnowledgeSource(str, Enum):
    """Source of knowledge entry."""
    
    USER = "user"
    AUTO_GENERATED = "auto_generated"
    SUGGESTED = "suggested"
    IMPORTED = "imported"


@dataclass
class KnowledgeEntry:
    """A single knowledge entry."""
    
    id: str
    title: str
    trigger_description: str
    content: str
    scope: KnowledgeScope
    pinned_repos: List[str]
    source: KnowledgeSource
    created_at: datetime
    updated_at: datetime
    created_by: str
    tags: List[str] = field(default_factory=list)
    is_active: bool = True
    access_count: int = 0
    last_accessed: Optional[datetime] = None
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "trigger_description": self.trigger_description,
            "content": self.content,
            "scope": self.scope.value,
            "pinned_repos": self.pinned_repos,
            "source": self.source.value,
            "created_at": self.created_at.isoformat(),
            "updated_at": self.updated_at.isoformat(),
            "created_by": self.created_by,
            "tags": self.tags,
            "is_active": self.is_active,
            "access_count": self.access_count,
            "last_accessed": self.last_accessed.isoformat() if self.last_accessed else None,
        }


@dataclass
class KnowledgeSuggestion:
    """A suggested knowledge entry from AI."""
    
    id: str
    title: str
    trigger_description: str
    content: str
    suggested_scope: KnowledgeScope
    suggested_repos: List[str]
    source_session_id: str
    source_message: str
    created_at: datetime
    status: str = "pending"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "id": self.id,
            "title": self.title,
            "trigger_description": self.trigger_description,
            "content": self.content,
            "suggested_scope": self.suggested_scope.value,
            "suggested_repos": self.suggested_repos,
            "source_session_id": self.source_session_id,
            "source_message": self.source_message,
            "created_at": self.created_at.isoformat(),
            "status": self.status,
        }


class KnowledgeStore:
    """In-memory knowledge store."""
    
    def __init__(self) -> None:
        self._entries: Dict[str, KnowledgeEntry] = {}
        self._suggestions: Dict[str, KnowledgeSuggestion] = {}
        self._populate_sample_knowledge()
    
    def _populate_sample_knowledge(self) -> None:
        """Populate with sample knowledge entries."""
        sample_entries = [
            {
                "title": "Python Code Style",
                "trigger_description": "When writing Python code, formatting, or reviewing Python files",
                "content": "Follow PEP 8 style guidelines. Use type hints for function parameters and return values. Prefer f-strings over .format() or % formatting. Use descriptive variable names. Keep functions small and focused on a single task.",
                "scope": KnowledgeScope.ALL_REPOS,
                "pinned_repos": [],
                "tags": ["python", "code-style", "best-practices"],
            },
            {
                "title": "Git Commit Messages",
                "trigger_description": "When creating git commits or writing commit messages",
                "content": "Use conventional commit format: type(scope): description. Types include feat, fix, docs, style, refactor, test, chore. Keep the subject line under 50 characters. Use imperative mood (Add feature, not Added feature). Include a body for complex changes explaining the why.",
                "scope": KnowledgeScope.ALL_REPOS,
                "pinned_repos": [],
                "tags": ["git", "commits", "conventions"],
            },
            {
                "title": "PR Review Guidelines",
                "trigger_description": "When creating pull requests or reviewing code",
                "content": "PRs should have a clear title and description. Include screenshots for UI changes. Link related issues. Keep PRs focused and small when possible. Ensure all tests pass before requesting review. Address all review comments before merging.",
                "scope": KnowledgeScope.ALL_REPOS,
                "pinned_repos": [],
                "tags": ["pr", "code-review", "github"],
            },
            {
                "title": "Testing Best Practices",
                "trigger_description": "When writing tests, unit tests, or integration tests",
                "content": "Write tests for all new features and bug fixes. Follow the Arrange-Act-Assert pattern. Use descriptive test names that explain what is being tested. Mock external dependencies. Aim for high coverage but prioritize critical paths.",
                "scope": KnowledgeScope.ALL_REPOS,
                "pinned_repos": [],
                "tags": ["testing", "unit-tests", "quality"],
            },
            {
                "title": "Error Handling",
                "trigger_description": "When handling errors, exceptions, or error messages",
                "content": "Always handle errors gracefully. Provide meaningful error messages to users. Log errors with sufficient context for debugging. Use specific exception types rather than generic ones. Don't swallow exceptions silently.",
                "scope": KnowledgeScope.ALL_REPOS,
                "pinned_repos": [],
                "tags": ["errors", "exceptions", "debugging"],
            },
            {
                "title": "API Design",
                "trigger_description": "When designing APIs, REST endpoints, or backend routes",
                "content": "Use RESTful conventions. Use appropriate HTTP methods (GET, POST, PUT, DELETE). Return consistent response formats. Include proper status codes. Document all endpoints. Version your APIs.",
                "scope": KnowledgeScope.ALL_REPOS,
                "pinned_repos": [],
                "tags": ["api", "rest", "backend"],
            },
            {
                "title": "Security Practices",
                "trigger_description": "When handling security, authentication, or sensitive data",
                "content": "Never commit secrets or credentials. Use environment variables for sensitive configuration. Validate and sanitize all user input. Use HTTPS for all communications. Implement proper authentication and authorization. Follow the principle of least privilege.",
                "scope": KnowledgeScope.ALL_REPOS,
                "pinned_repos": [],
                "tags": ["security", "authentication", "secrets"],
            },
            {
                "title": "React Component Guidelines",
                "trigger_description": "When writing React components or frontend code",
                "content": "Use functional components with hooks. Keep components small and focused. Use TypeScript for type safety. Extract reusable logic into custom hooks. Use proper state management. Follow the component composition pattern.",
                "scope": KnowledgeScope.SPECIFIC_REPOS,
                "pinned_repos": ["frontend", "web-app"],
                "tags": ["react", "frontend", "components"],
            },
            {
                "title": "Database Queries",
                "trigger_description": "When writing database queries or working with databases",
                "content": "Use parameterized queries to prevent SQL injection. Index frequently queried columns. Avoid N+1 query problems. Use transactions for related operations. Optimize queries for performance. Use appropriate data types.",
                "scope": KnowledgeScope.ALL_REPOS,
                "pinned_repos": [],
                "tags": ["database", "sql", "performance"],
            },
            {
                "title": "Documentation Standards",
                "trigger_description": "When writing documentation, README files, or code comments",
                "content": "Keep documentation up to date with code changes. Include setup instructions in README. Document public APIs and interfaces. Use clear and concise language. Include examples where helpful. Document edge cases and limitations.",
                "scope": KnowledgeScope.ALL_REPOS,
                "pinned_repos": [],
                "tags": ["documentation", "readme", "comments"],
            },
        ]
        
        for entry_data in sample_entries:
            entry_id = str(uuid.uuid4())
            now = datetime.utcnow()
            entry = KnowledgeEntry(
                id=entry_id,
                title=entry_data["title"],
                trigger_description=entry_data["trigger_description"],
                content=entry_data["content"],
                scope=entry_data["scope"],
                pinned_repos=entry_data["pinned_repos"],
                source=KnowledgeSource.AUTO_GENERATED,
                created_at=now,
                updated_at=now,
                created_by="system",
                tags=entry_data["tags"],
            )
            self._entries[entry_id] = entry
    
    def get_all(self) -> List[KnowledgeEntry]:
        """Get all knowledge entries."""
        return list(self._entries.values())
    
    def get_by_id(self, entry_id: str) -> Optional[KnowledgeEntry]:
        """Get a knowledge entry by ID."""
        return self._entries.get(entry_id)
    
    def create(
        self,
        title: str,
        trigger_description: str,
        content: str,
        scope: KnowledgeScope = KnowledgeScope.NO_REPOS,
        pinned_repos: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        created_by: str = "user",
        source: KnowledgeSource = KnowledgeSource.USER,
    ) -> KnowledgeEntry:
        """Create a new knowledge entry."""
        entry_id = str(uuid.uuid4())
        now = datetime.utcnow()
        entry = KnowledgeEntry(
            id=entry_id,
            title=title,
            trigger_description=trigger_description,
            content=content,
            scope=scope,
            pinned_repos=pinned_repos or [],
            source=source,
            created_at=now,
            updated_at=now,
            created_by=created_by,
            tags=tags or [],
        )
        self._entries[entry_id] = entry
        return entry
    
    def update(
        self,
        entry_id: str,
        title: Optional[str] = None,
        trigger_description: Optional[str] = None,
        content: Optional[str] = None,
        scope: Optional[KnowledgeScope] = None,
        pinned_repos: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
    ) -> Optional[KnowledgeEntry]:
        """Update a knowledge entry."""
        entry = self._entries.get(entry_id)
        if not entry:
            return None
        
        if title is not None:
            entry.title = title
        if trigger_description is not None:
            entry.trigger_description = trigger_description
        if content is not None:
            entry.content = content
        if scope is not None:
            entry.scope = scope
        if pinned_repos is not None:
            entry.pinned_repos = pinned_repos
        if tags is not None:
            entry.tags = tags
        if is_active is not None:
            entry.is_active = is_active
        
        entry.updated_at = datetime.utcnow()
        return entry
    
    def delete(self, entry_id: str) -> bool:
        """Delete a knowledge entry."""
        if entry_id in self._entries:
            del self._entries[entry_id]
            return True
        return False
    
    def search(self, query: str) -> List[KnowledgeEntry]:
        """Search knowledge entries by query."""
        query_lower = query.lower()
        results = []
        for entry in self._entries.values():
            if not entry.is_active:
                continue
            if (
                query_lower in entry.title.lower()
                or query_lower in entry.trigger_description.lower()
                or query_lower in entry.content.lower()
                or any(query_lower in tag.lower() for tag in entry.tags)
            ):
                results.append(entry)
        return results
    
    def get_by_repo(self, repo: str) -> List[KnowledgeEntry]:
        """Get knowledge entries applicable to a specific repo."""
        results = []
        for entry in self._entries.values():
            if not entry.is_active:
                continue
            if entry.scope == KnowledgeScope.ALL_REPOS:
                results.append(entry)
            elif entry.scope == KnowledgeScope.SPECIFIC_REPOS:
                if repo in entry.pinned_repos:
                    results.append(entry)
        return results
    
    def get_relevant(self, context: str, repo: Optional[str] = None) -> List[KnowledgeEntry]:
        """Get knowledge entries relevant to the given context."""
        context_lower = context.lower()
        results = []
        
        for entry in self._entries.values():
            if not entry.is_active:
                continue
            
            if repo:
                if entry.scope == KnowledgeScope.SPECIFIC_REPOS:
                    if repo not in entry.pinned_repos:
                        continue
            
            trigger_words = entry.trigger_description.lower().split()
            relevance_score = sum(1 for word in trigger_words if word in context_lower)
            
            if relevance_score > 0:
                entry.access_count += 1
                entry.last_accessed = datetime.utcnow()
                results.append((entry, relevance_score))
        
        results.sort(key=lambda x: x[1], reverse=True)
        return [entry for entry, _ in results[:5]]
    
    def get_by_tag(self, tag: str) -> List[KnowledgeEntry]:
        """Get knowledge entries by tag."""
        tag_lower = tag.lower()
        return [
            entry for entry in self._entries.values()
            if entry.is_active and any(tag_lower == t.lower() for t in entry.tags)
        ]
    
    def get_all_tags(self) -> List[str]:
        """Get all unique tags."""
        tags = set()
        for entry in self._entries.values():
            tags.update(entry.tags)
        return sorted(tags)
    
    def add_suggestion(
        self,
        title: str,
        trigger_description: str,
        content: str,
        suggested_scope: KnowledgeScope,
        suggested_repos: List[str],
        source_session_id: str,
        source_message: str,
    ) -> KnowledgeSuggestion:
        """Add a knowledge suggestion."""
        suggestion_id = str(uuid.uuid4())
        suggestion = KnowledgeSuggestion(
            id=suggestion_id,
            title=title,
            trigger_description=trigger_description,
            content=content,
            suggested_scope=suggested_scope,
            suggested_repos=suggested_repos,
            source_session_id=source_session_id,
            source_message=source_message,
            created_at=datetime.utcnow(),
        )
        self._suggestions[suggestion_id] = suggestion
        return suggestion
    
    def get_suggestions(self, status: Optional[str] = None) -> List[KnowledgeSuggestion]:
        """Get all knowledge suggestions."""
        if status:
            return [s for s in self._suggestions.values() if s.status == status]
        return list(self._suggestions.values())
    
    def get_suggestion_by_id(self, suggestion_id: str) -> Optional[KnowledgeSuggestion]:
        """Get a suggestion by ID."""
        return self._suggestions.get(suggestion_id)
    
    def accept_suggestion(self, suggestion_id: str) -> Optional[KnowledgeEntry]:
        """Accept a suggestion and create a knowledge entry."""
        suggestion = self._suggestions.get(suggestion_id)
        if not suggestion:
            return None
        
        entry = self.create(
            title=suggestion.title,
            trigger_description=suggestion.trigger_description,
            content=suggestion.content,
            scope=suggestion.suggested_scope,
            pinned_repos=suggestion.suggested_repos,
            source=KnowledgeSource.SUGGESTED,
            created_by="ai_suggestion",
        )
        
        suggestion.status = "accepted"
        return entry
    
    def dismiss_suggestion(self, suggestion_id: str) -> bool:
        """Dismiss a suggestion."""
        suggestion = self._suggestions.get(suggestion_id)
        if not suggestion:
            return False
        suggestion.status = "dismissed"
        return True
    
    def delete_suggestion(self, suggestion_id: str) -> bool:
        """Delete a suggestion."""
        if suggestion_id in self._suggestions:
            del self._suggestions[suggestion_id]
            return True
        return False


knowledge_store = KnowledgeStore()


class KnowledgeTool(BaseTool):
    """Tool for managing organizational knowledge."""
    
    name = "knowledge"
    description = """Manage organizational knowledge that can be referenced across sessions.
    
    Operations:
    - list: List all knowledge entries
    - get: Get a specific knowledge entry by ID
    - create: Create a new knowledge entry
    - update: Update an existing knowledge entry
    - delete: Delete a knowledge entry
    - search: Search knowledge entries
    - get_relevant: Get knowledge relevant to a context
    - get_by_repo: Get knowledge for a specific repository
    - get_by_tag: Get knowledge by tag
    - get_tags: Get all available tags
    - suggest: Create a knowledge suggestion
    - list_suggestions: List all suggestions
    - accept_suggestion: Accept a suggestion
    - dismiss_suggestion: Dismiss a suggestion
    """
    
    async def execute(self, **kwargs: Any) -> Dict[str, Any]:
        """Execute knowledge operations."""
        command = kwargs.get("command", "list")
        
        if command == "list":
            return await self._list_knowledge(**kwargs)
        elif command == "get":
            return await self._get_knowledge(**kwargs)
        elif command == "create":
            return await self._create_knowledge(**kwargs)
        elif command == "update":
            return await self._update_knowledge(**kwargs)
        elif command == "delete":
            return await self._delete_knowledge(**kwargs)
        elif command == "search":
            return await self._search_knowledge(**kwargs)
        elif command == "get_relevant":
            return await self._get_relevant_knowledge(**kwargs)
        elif command == "get_by_repo":
            return await self._get_by_repo(**kwargs)
        elif command == "get_by_tag":
            return await self._get_by_tag(**kwargs)
        elif command == "get_tags":
            return await self._get_tags()
        elif command == "suggest":
            return await self._suggest_knowledge(**kwargs)
        elif command == "list_suggestions":
            return await self._list_suggestions(**kwargs)
        elif command == "accept_suggestion":
            return await self._accept_suggestion(**kwargs)
        elif command == "dismiss_suggestion":
            return await self._dismiss_suggestion(**kwargs)
        else:
            return {"error": f"Unknown command: {command}"}
    
    async def _list_knowledge(
        self,
        page: int = 1,
        per_page: int = 20,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List all knowledge entries with pagination."""
        entries = knowledge_store.get_all()
        total = len(entries)
        
        start = (page - 1) * per_page
        end = start + per_page
        paginated = entries[start:end]
        
        return {
            "entries": [e.to_dict() for e in paginated],
            "total": total,
            "page": page,
            "per_page": per_page,
            "total_pages": (total + per_page - 1) // per_page,
        }
    
    async def _get_knowledge(self, entry_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Get a specific knowledge entry."""
        entry = knowledge_store.get_by_id(entry_id)
        if not entry:
            return {"error": f"Knowledge entry not found: {entry_id}"}
        return {"entry": entry.to_dict()}
    
    async def _create_knowledge(
        self,
        title: str,
        trigger_description: str,
        content: str,
        scope: str = "no_repos",
        pinned_repos: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a new knowledge entry."""
        try:
            scope_enum = KnowledgeScope(scope)
        except ValueError:
            return {"error": f"Invalid scope: {scope}"}
        
        entry = knowledge_store.create(
            title=title,
            trigger_description=trigger_description,
            content=content,
            scope=scope_enum,
            pinned_repos=pinned_repos,
            tags=tags,
        )
        return {"entry": entry.to_dict(), "message": "Knowledge entry created successfully"}
    
    async def _update_knowledge(
        self,
        entry_id: str,
        title: Optional[str] = None,
        trigger_description: Optional[str] = None,
        content: Optional[str] = None,
        scope: Optional[str] = None,
        pinned_repos: Optional[List[str]] = None,
        tags: Optional[List[str]] = None,
        is_active: Optional[bool] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Update a knowledge entry."""
        scope_enum = None
        if scope:
            try:
                scope_enum = KnowledgeScope(scope)
            except ValueError:
                return {"error": f"Invalid scope: {scope}"}
        
        entry = knowledge_store.update(
            entry_id=entry_id,
            title=title,
            trigger_description=trigger_description,
            content=content,
            scope=scope_enum,
            pinned_repos=pinned_repos,
            tags=tags,
            is_active=is_active,
        )
        
        if not entry:
            return {"error": f"Knowledge entry not found: {entry_id}"}
        
        return {"entry": entry.to_dict(), "message": "Knowledge entry updated successfully"}
    
    async def _delete_knowledge(self, entry_id: str, **kwargs: Any) -> Dict[str, Any]:
        """Delete a knowledge entry."""
        if knowledge_store.delete(entry_id):
            return {"message": f"Knowledge entry {entry_id} deleted successfully"}
        return {"error": f"Knowledge entry not found: {entry_id}"}
    
    async def _search_knowledge(self, query: str, **kwargs: Any) -> Dict[str, Any]:
        """Search knowledge entries."""
        entries = knowledge_store.search(query)
        return {
            "entries": [e.to_dict() for e in entries],
            "total": len(entries),
            "query": query,
        }
    
    async def _get_relevant_knowledge(
        self,
        context: str,
        repo: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get knowledge relevant to a context."""
        entries = knowledge_store.get_relevant(context, repo)
        return {
            "entries": [e.to_dict() for e in entries],
            "total": len(entries),
            "context": context,
            "repo": repo,
        }
    
    async def _get_by_repo(self, repo: str, **kwargs: Any) -> Dict[str, Any]:
        """Get knowledge for a specific repository."""
        entries = knowledge_store.get_by_repo(repo)
        return {
            "entries": [e.to_dict() for e in entries],
            "total": len(entries),
            "repo": repo,
        }
    
    async def _get_by_tag(self, tag: str, **kwargs: Any) -> Dict[str, Any]:
        """Get knowledge by tag."""
        entries = knowledge_store.get_by_tag(tag)
        return {
            "entries": [e.to_dict() for e in entries],
            "total": len(entries),
            "tag": tag,
        }
    
    async def _get_tags(self) -> Dict[str, Any]:
        """Get all available tags."""
        tags = knowledge_store.get_all_tags()
        return {"tags": tags, "total": len(tags)}
    
    async def _suggest_knowledge(
        self,
        title: str,
        trigger_description: str,
        content: str,
        suggested_scope: str = "no_repos",
        suggested_repos: Optional[List[str]] = None,
        source_session_id: str = "",
        source_message: str = "",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a knowledge suggestion."""
        try:
            scope_enum = KnowledgeScope(suggested_scope)
        except ValueError:
            return {"error": f"Invalid scope: {suggested_scope}"}
        
        suggestion = knowledge_store.add_suggestion(
            title=title,
            trigger_description=trigger_description,
            content=content,
            suggested_scope=scope_enum,
            suggested_repos=suggested_repos or [],
            source_session_id=source_session_id,
            source_message=source_message,
        )
        return {
            "suggestion": suggestion.to_dict(),
            "message": "Knowledge suggestion created successfully",
        }
    
    async def _list_suggestions(
        self,
        status: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List all knowledge suggestions."""
        suggestions = knowledge_store.get_suggestions(status)
        return {
            "suggestions": [s.to_dict() for s in suggestions],
            "total": len(suggestions),
        }
    
    async def _accept_suggestion(
        self,
        suggestion_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Accept a knowledge suggestion."""
        entry = knowledge_store.accept_suggestion(suggestion_id)
        if not entry:
            return {"error": f"Suggestion not found: {suggestion_id}"}
        return {
            "entry": entry.to_dict(),
            "message": "Suggestion accepted and knowledge entry created",
        }
    
    async def _dismiss_suggestion(
        self,
        suggestion_id: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Dismiss a knowledge suggestion."""
        if knowledge_store.dismiss_suggestion(suggestion_id):
            return {"message": f"Suggestion {suggestion_id} dismissed"}
        return {"error": f"Suggestion not found: {suggestion_id}"}
