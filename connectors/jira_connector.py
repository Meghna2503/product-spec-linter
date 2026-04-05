import os, urllib.request, urllib.parse, json, base64
from typing import Dict, List

class JiraConnector:
    def __init__(self, jira_url=None, email=None, api_token=None):
        self.jira_url = (jira_url or os.environ.get("JIRA_URL","")).rstrip("/")
        self.email = email or os.environ.get("JIRA_EMAIL","")
        self.api_token = api_token or os.environ.get("JIRA_API_TOKEN","")
        if not all([self.jira_url, self.email, self.api_token]):
            raise ValueError("Missing Jira credentials. Set JIRA_URL, JIRA_EMAIL, JIRA_API_TOKEN")
        creds = base64.b64encode(f"{self.email}:{self.api_token}".encode()).decode()
        self.auth_header = f"Basic {creds}"

    def _get(self, path):
        req = urllib.request.Request(f"{self.jira_url}/rest/api/3/{path}",
            headers={"Authorization": self.auth_header, "Accept": "application/json"})
        with urllib.request.urlopen(req, timeout=30) as r:
            return json.loads(r.read())

    def get_story(self, key): return self._extract(self._get(f"issue/{key}"))

    def get_epic_stories(self, key):
        raw = self._get(f"issue/{key}")
        fields = raw.get("fields", {})
        epic_key = None
        for field in ["parent","customfield_10014","customfield_10008"]:
            val = fields.get(field)
            if isinstance(val, dict): epic_key = val.get("key")
            elif isinstance(val, str) and "-" in str(val): epic_key = val
            if epic_key: break
        if not epic_key: return [self._extract(raw)]
        jql = urllib.parse.quote(f'"Epic Link"="{epic_key}" OR parent="{epic_key}"')
        data = self._get(f"search?jql={jql}&maxResults=50")
        return [self._extract(i) for i in data.get("issues", [])]

    def _extract(self, issue):
        f = issue.get("fields", {})
        return {"key": issue.get("key",""), "summary": f.get("summary",""),
                "description": self._text(f.get("description","")),
                "acceptance_criteria": self._text(f.get("customfield_10016") or f.get("customfield_10033") or ""),
                "status": f.get("status",{}).get("name",""), "type": f.get("issuetype",{}).get("name","Story")}

    def _text(self, c):
        if not c: return ""
        if isinstance(c, str): return c
        if isinstance(c, dict): return self._adf(c)
        return str(c)

    def _adf(self, node):
        if node.get("type") == "text": return node.get("text","")
        return " ".join(filter(None,[self._adf(c) for c in node.get("content",[])]))

    def format_for_linter(self, stories, focus_key=None):
        lines = [f"FOCUS STORY: {focus_key}\nCONTEXT STORIES:\n"] if focus_key else []
        for s in stories:
            marker = ">>> FOCUS <<<" if s["key"]==focus_key else ""
            lines += [f"{'='*40}", f"[{s['key']}] {marker} {s['summary']}",
                      f"Status: {s['status']}",
                      f"Description: {s['description']}" if s['description'] else "",
                      f"ACs: {s['acceptance_criteria']}" if s['acceptance_criteria'] else "", ""]
        return "\n".join(lines)