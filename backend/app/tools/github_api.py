"""GitHub API tool for PR management and CI checks."""

import os
from typing import Any, Dict, List, Optional

import httpx

from app.tools.base import BaseTool


class GitHubAPITool(BaseTool):
    """Tool for GitHub API operations like PR management and CI checks."""

    name = "github_api"
    description = "Interact with GitHub API for PR management, CI checks, and comments"

    def __init__(self):
        self.base_url = "https://api.github.com"
        self.token = os.environ.get("GITHUB_TOKEN")

    def _get_headers(self) -> Dict[str, str]:
        """Get headers for GitHub API requests."""
        headers = {
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if self.token:
            headers["Authorization"] = f"Bearer {self.token}"
        return headers

    async def execute(self, operation: str, **kwargs: Any) -> Dict[str, Any]:
        """Execute a GitHub API operation."""
        operations = {
            "create_pr": self.create_pr,
            "view_pr": self.view_pr,
            "update_pr": self.update_pr,
            "merge_pr": self.merge_pr,
            "list_prs": self.list_prs,
            "pr_checks": self.get_pr_checks,
            "ci_job_logs": self.get_ci_job_logs,
            "comment_on_pr": self.comment_on_pr,
            "list_pr_comments": self.list_pr_comments,
            "get_pr_diff": self.get_pr_diff,
            "list_repos": self.list_repos,
            "get_repo": self.get_repo,
            "create_issue": self.create_issue,
            "list_issues": self.list_issues,
        }

        if operation not in operations:
            return {"error": f"Unknown operation: {operation}"}

        if not self.token:
            return {
                "error": "GITHUB_TOKEN environment variable not set. Please set it to use GitHub API features."
            }

        return await operations[operation](**kwargs)

    async def create_pr(
        self,
        repo: str,
        title: str,
        head_branch: str,
        base_branch: str,
        body: Optional[str] = None,
        draft: bool = False,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create a pull request.
        
        Args:
            repo: Repository in owner/repo format
            title: PR title
            head_branch: Branch to merge from
            base_branch: Branch to merge into
            body: PR description
            draft: Whether to create as draft PR
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/repos/{repo}/pulls",
                    headers=self._get_headers(),
                    json={
                        "title": title,
                        "head": head_branch,
                        "base": base_branch,
                        "body": body or "",
                        "draft": draft,
                    },
                    timeout=30.0,
                )

                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "pr_number": data["number"],
                        "url": data["html_url"],
                        "state": data["state"],
                        "title": data["title"],
                        "created_at": data["created_at"],
                    }
                else:
                    return {
                        "error": f"Failed to create PR: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}

    async def view_pr(
        self,
        repo: str,
        pull_number: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """View details of a pull request.
        
        Args:
            repo: Repository in owner/repo format
            pull_number: PR number
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo}/pulls/{pull_number}",
                    headers=self._get_headers(),
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "pr_number": data["number"],
                        "title": data["title"],
                        "body": data["body"],
                        "state": data["state"],
                        "url": data["html_url"],
                        "head_branch": data["head"]["ref"],
                        "base_branch": data["base"]["ref"],
                        "author": data["user"]["login"],
                        "created_at": data["created_at"],
                        "updated_at": data["updated_at"],
                        "merged": data.get("merged", False),
                        "mergeable": data.get("mergeable"),
                        "additions": data.get("additions", 0),
                        "deletions": data.get("deletions", 0),
                        "changed_files": data.get("changed_files", 0),
                    }
                else:
                    return {
                        "error": f"Failed to get PR: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}

    async def update_pr(
        self,
        repo: str,
        pull_number: int,
        title: Optional[str] = None,
        body: Optional[str] = None,
        state: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Update a pull request.
        
        Args:
            repo: Repository in owner/repo format
            pull_number: PR number
            title: New title (optional)
            body: New description (optional)
            state: New state - 'open' or 'closed' (optional)
        """
        try:
            update_data: Dict[str, Any] = {}
            if title:
                update_data["title"] = title
            if body:
                update_data["body"] = body
            if state:
                update_data["state"] = state

            if not update_data:
                return {"error": "No update parameters provided"}

            async with httpx.AsyncClient() as client:
                response = await client.patch(
                    f"{self.base_url}/repos/{repo}/pulls/{pull_number}",
                    headers=self._get_headers(),
                    json=update_data,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "pr_number": data["number"],
                        "url": data["html_url"],
                        "state": data["state"],
                        "title": data["title"],
                    }
                else:
                    return {
                        "error": f"Failed to update PR: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}

    async def merge_pr(
        self,
        repo: str,
        pull_number: int,
        commit_title: Optional[str] = None,
        commit_message: Optional[str] = None,
        merge_method: str = "merge",
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Merge a pull request.
        
        Args:
            repo: Repository in owner/repo format
            pull_number: PR number
            commit_title: Title for merge commit
            commit_message: Message for merge commit
            merge_method: 'merge', 'squash', or 'rebase'
        """
        try:
            merge_data: Dict[str, Any] = {"merge_method": merge_method}
            if commit_title:
                merge_data["commit_title"] = commit_title
            if commit_message:
                merge_data["commit_message"] = commit_message

            async with httpx.AsyncClient() as client:
                response = await client.put(
                    f"{self.base_url}/repos/{repo}/pulls/{pull_number}/merge",
                    headers=self._get_headers(),
                    json=merge_data,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "merged": data.get("merged", True),
                        "message": data.get("message", "PR merged successfully"),
                        "sha": data.get("sha"),
                    }
                else:
                    return {
                        "error": f"Failed to merge PR: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}

    async def list_prs(
        self,
        repo: str,
        state: str = "open",
        per_page: int = 30,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List pull requests for a repository.
        
        Args:
            repo: Repository in owner/repo format
            state: 'open', 'closed', or 'all'
            per_page: Number of results per page (max 100)
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo}/pulls",
                    headers=self._get_headers(),
                    params={"state": state, "per_page": min(per_page, 100)},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    prs = [
                        {
                            "number": pr["number"],
                            "title": pr["title"],
                            "state": pr["state"],
                            "author": pr["user"]["login"],
                            "url": pr["html_url"],
                            "created_at": pr["created_at"],
                            "head_branch": pr["head"]["ref"],
                            "base_branch": pr["base"]["ref"],
                        }
                        for pr in data
                    ]
                    return {
                        "success": True,
                        "pull_requests": prs,
                        "count": len(prs),
                    }
                else:
                    return {
                        "error": f"Failed to list PRs: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}

    async def get_pr_checks(
        self,
        repo: str,
        pull_number: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get CI check status for a pull request.
        
        Args:
            repo: Repository in owner/repo format
            pull_number: PR number
        """
        try:
            async with httpx.AsyncClient() as client:
                # First get the PR to get the head SHA
                pr_response = await client.get(
                    f"{self.base_url}/repos/{repo}/pulls/{pull_number}",
                    headers=self._get_headers(),
                    timeout=30.0,
                )

                if pr_response.status_code != 200:
                    return {
                        "error": f"Failed to get PR: {pr_response.status_code}",
                        "details": pr_response.json(),
                    }

                pr_data = pr_response.json()
                head_sha = pr_data["head"]["sha"]

                # Get check runs for the commit
                checks_response = await client.get(
                    f"{self.base_url}/repos/{repo}/commits/{head_sha}/check-runs",
                    headers=self._get_headers(),
                    timeout=30.0,
                )

                if checks_response.status_code != 200:
                    return {
                        "error": f"Failed to get checks: {checks_response.status_code}",
                        "details": checks_response.json(),
                    }

                checks_data = checks_response.json()
                check_runs = [
                    {
                        "id": check["id"],
                        "name": check["name"],
                        "status": check["status"],
                        "conclusion": check.get("conclusion"),
                        "started_at": check.get("started_at"),
                        "completed_at": check.get("completed_at"),
                        "url": check.get("html_url"),
                    }
                    for check in checks_data.get("check_runs", [])
                ]

                # Determine overall status
                all_completed = all(c["status"] == "completed" for c in check_runs)
                all_passed = all(c["conclusion"] == "success" for c in check_runs if c["conclusion"])

                return {
                    "success": True,
                    "head_sha": head_sha,
                    "check_runs": check_runs,
                    "total_count": len(check_runs),
                    "all_completed": all_completed,
                    "all_passed": all_passed if all_completed else None,
                }
        except Exception as e:
            return {"error": str(e)}

    async def get_ci_job_logs(
        self,
        repo: str,
        job_id: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get logs for a specific CI job.
        
        Args:
            repo: Repository in owner/repo format
            job_id: The job ID from check runs
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get job details
                job_response = await client.get(
                    f"{self.base_url}/repos/{repo}/actions/jobs/{job_id}",
                    headers=self._get_headers(),
                    timeout=30.0,
                )

                if job_response.status_code != 200:
                    return {
                        "error": f"Failed to get job: {job_response.status_code}",
                        "details": job_response.json(),
                    }

                job_data = job_response.json()

                # Get job logs
                logs_headers = self._get_headers()
                logs_headers["Accept"] = "application/vnd.github+json"

                logs_response = await client.get(
                    f"{self.base_url}/repos/{repo}/actions/jobs/{job_id}/logs",
                    headers=logs_headers,
                    timeout=60.0,
                    follow_redirects=True,
                )

                logs = ""
                if logs_response.status_code == 200:
                    logs = logs_response.text
                elif logs_response.status_code == 302:
                    # Follow redirect for logs
                    redirect_url = logs_response.headers.get("Location")
                    if redirect_url:
                        redirect_response = await client.get(redirect_url, timeout=60.0)
                        logs = redirect_response.text

                return {
                    "success": True,
                    "job_id": job_id,
                    "name": job_data.get("name"),
                    "status": job_data.get("status"),
                    "conclusion": job_data.get("conclusion"),
                    "started_at": job_data.get("started_at"),
                    "completed_at": job_data.get("completed_at"),
                    "logs": logs[:50000] if logs else "No logs available",
                }
        except Exception as e:
            return {"error": str(e)}

    async def comment_on_pr(
        self,
        repo: str,
        pull_number: int,
        body: str,
        path: Optional[str] = None,
        line: Optional[int] = None,
        commit_id: Optional[str] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Comment on a pull request.
        
        Args:
            repo: Repository in owner/repo format
            pull_number: PR number
            body: Comment body (markdown supported)
            path: File path for inline comment (optional)
            line: Line number for inline comment (optional)
            commit_id: Commit SHA for inline comment (optional)
        """
        try:
            async with httpx.AsyncClient() as client:
                if path and line and commit_id:
                    # Create a review comment (inline)
                    response = await client.post(
                        f"{self.base_url}/repos/{repo}/pulls/{pull_number}/comments",
                        headers=self._get_headers(),
                        json={
                            "body": body,
                            "path": path,
                            "line": line,
                            "commit_id": commit_id,
                        },
                        timeout=30.0,
                    )
                else:
                    # Create an issue comment (general)
                    response = await client.post(
                        f"{self.base_url}/repos/{repo}/issues/{pull_number}/comments",
                        headers=self._get_headers(),
                        json={"body": body},
                        timeout=30.0,
                    )

                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "comment_id": data["id"],
                        "url": data["html_url"],
                        "created_at": data["created_at"],
                    }
                else:
                    return {
                        "error": f"Failed to create comment: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}

    async def list_pr_comments(
        self,
        repo: str,
        pull_number: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List comments on a pull request.
        
        Args:
            repo: Repository in owner/repo format
            pull_number: PR number
        """
        try:
            async with httpx.AsyncClient() as client:
                # Get issue comments (general comments)
                issue_comments_response = await client.get(
                    f"{self.base_url}/repos/{repo}/issues/{pull_number}/comments",
                    headers=self._get_headers(),
                    timeout=30.0,
                )

                # Get review comments (inline comments)
                review_comments_response = await client.get(
                    f"{self.base_url}/repos/{repo}/pulls/{pull_number}/comments",
                    headers=self._get_headers(),
                    timeout=30.0,
                )

                comments: List[Dict[str, Any]] = []

                if issue_comments_response.status_code == 200:
                    for comment in issue_comments_response.json():
                        comments.append({
                            "id": comment["id"],
                            "type": "issue_comment",
                            "author": comment["user"]["login"],
                            "body": comment["body"],
                            "created_at": comment["created_at"],
                            "url": comment["html_url"],
                        })

                if review_comments_response.status_code == 200:
                    for comment in review_comments_response.json():
                        comments.append({
                            "id": comment["id"],
                            "type": "review_comment",
                            "author": comment["user"]["login"],
                            "body": comment["body"],
                            "path": comment.get("path"),
                            "line": comment.get("line"),
                            "created_at": comment["created_at"],
                            "url": comment["html_url"],
                        })

                # Sort by created_at
                comments.sort(key=lambda x: x["created_at"])

                return {
                    "success": True,
                    "comments": comments,
                    "count": len(comments),
                }
        except Exception as e:
            return {"error": str(e)}

    async def get_pr_diff(
        self,
        repo: str,
        pull_number: int,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get the diff for a pull request.
        
        Args:
            repo: Repository in owner/repo format
            pull_number: PR number
        """
        try:
            async with httpx.AsyncClient() as client:
                headers = self._get_headers()
                headers["Accept"] = "application/vnd.github.diff"

                response = await client.get(
                    f"{self.base_url}/repos/{repo}/pulls/{pull_number}",
                    headers=headers,
                    timeout=30.0,
                )

                if response.status_code == 200:
                    return {
                        "success": True,
                        "diff": response.text[:100000],
                    }
                else:
                    return {
                        "error": f"Failed to get diff: {response.status_code}",
                    }
        except Exception as e:
            return {"error": str(e)}

    async def list_repos(
        self,
        user: Optional[str] = None,
        org: Optional[str] = None,
        per_page: int = 30,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List repositories for a user or organization.
        
        Args:
            user: GitHub username (optional, defaults to authenticated user)
            org: Organization name (optional)
            per_page: Number of results per page
        """
        try:
            async with httpx.AsyncClient() as client:
                if org:
                    url = f"{self.base_url}/orgs/{org}/repos"
                elif user:
                    url = f"{self.base_url}/users/{user}/repos"
                else:
                    url = f"{self.base_url}/user/repos"

                response = await client.get(
                    url,
                    headers=self._get_headers(),
                    params={"per_page": min(per_page, 100)},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    repos = [
                        {
                            "name": repo["name"],
                            "full_name": repo["full_name"],
                            "description": repo.get("description"),
                            "url": repo["html_url"],
                            "private": repo["private"],
                            "default_branch": repo.get("default_branch"),
                        }
                        for repo in data
                    ]
                    return {
                        "success": True,
                        "repositories": repos,
                        "count": len(repos),
                    }
                else:
                    return {
                        "error": f"Failed to list repos: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}

    async def get_repo(
        self,
        repo: str,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Get repository details.
        
        Args:
            repo: Repository in owner/repo format
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo}",
                    headers=self._get_headers(),
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    return {
                        "success": True,
                        "name": data["name"],
                        "full_name": data["full_name"],
                        "description": data.get("description"),
                        "url": data["html_url"],
                        "clone_url": data["clone_url"],
                        "ssh_url": data["ssh_url"],
                        "private": data["private"],
                        "default_branch": data.get("default_branch"),
                        "language": data.get("language"),
                        "stars": data.get("stargazers_count", 0),
                        "forks": data.get("forks_count", 0),
                        "open_issues": data.get("open_issues_count", 0),
                    }
                else:
                    return {
                        "error": f"Failed to get repo: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}

    async def create_issue(
        self,
        repo: str,
        title: str,
        body: Optional[str] = None,
        labels: Optional[List[str]] = None,
        assignees: Optional[List[str]] = None,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """Create an issue.
        
        Args:
            repo: Repository in owner/repo format
            title: Issue title
            body: Issue body (optional)
            labels: List of label names (optional)
            assignees: List of usernames to assign (optional)
        """
        try:
            issue_data: Dict[str, Any] = {"title": title}
            if body:
                issue_data["body"] = body
            if labels:
                issue_data["labels"] = labels
            if assignees:
                issue_data["assignees"] = assignees

            async with httpx.AsyncClient() as client:
                response = await client.post(
                    f"{self.base_url}/repos/{repo}/issues",
                    headers=self._get_headers(),
                    json=issue_data,
                    timeout=30.0,
                )

                if response.status_code == 201:
                    data = response.json()
                    return {
                        "success": True,
                        "issue_number": data["number"],
                        "url": data["html_url"],
                        "title": data["title"],
                        "state": data["state"],
                    }
                else:
                    return {
                        "error": f"Failed to create issue: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}

    async def list_issues(
        self,
        repo: str,
        state: str = "open",
        per_page: int = 30,
        **kwargs: Any,
    ) -> Dict[str, Any]:
        """List issues for a repository.
        
        Args:
            repo: Repository in owner/repo format
            state: 'open', 'closed', or 'all'
            per_page: Number of results per page
        """
        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.base_url}/repos/{repo}/issues",
                    headers=self._get_headers(),
                    params={"state": state, "per_page": min(per_page, 100)},
                    timeout=30.0,
                )

                if response.status_code == 200:
                    data = response.json()
                    issues = [
                        {
                            "number": issue["number"],
                            "title": issue["title"],
                            "state": issue["state"],
                            "author": issue["user"]["login"],
                            "url": issue["html_url"],
                            "created_at": issue["created_at"],
                            "labels": [label["name"] for label in issue.get("labels", [])],
                        }
                        for issue in data
                        if "pull_request" not in issue  # Exclude PRs
                    ]
                    return {
                        "success": True,
                        "issues": issues,
                        "count": len(issues),
                    }
                else:
                    return {
                        "error": f"Failed to list issues: {response.status_code}",
                        "details": response.json(),
                    }
        except Exception as e:
            return {"error": str(e)}
