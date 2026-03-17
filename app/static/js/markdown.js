const textarea = document.getElementById("markdown-input");
const preview = document.getElementById("preview-area");
const content1 = document.getElementById("content1");
const content2 = document.getElementById("content2");

function parse_markdown() {
  let md = textarea.value;

  if (md === "Select the Component to add!") {
    preview.innerHTML = "";
    return;
  }

  // Escape HTML
  md = md.replace(/</g, "&lt;");

  // HEADINGS
  md = md
    .replace(/^### (.*$)/gim, "<h3>$1</h3>")
    .replace(/^## (.*$)/gim, "<h2>$1</h2>")
    .replace(/^# (.*$)/gim, "<h1>$1</h1>");

  // INLINE FORMATTING
  md = md
    .replace(/\*\*(.*?)\*\*/gim, "<strong>$1</strong>")
    .replace(/\*(.*?)\*/gim, "<em>$1</em>")
    .replace(/==(.*?)==/gim, "<mark>$1</mark>")
    .replace(/~~(.*?)~~/gim, "<del>$1</del>");

  // BLOCK ELEMENTS
  md = md
    .replace(/^> (.*$)/gim, "<blockquote>$1</blockquote>")
    .replace(/^---$/gim, "<hr>");

  // CODE BLOCK
  md = md.replace(/```([\s\S]*?)```/gim, (_, code) => {
    return `<pre><code>${code.trim()}</code></pre>`;
  });

  // CODE INLINE
  md = md.replace(/`([^`]+)`/gim, "<code class='code-inline'>$1</code>");

  // IMAGES
  md = md.replace(/!\[(.*?)\]\((.*?)\)/gim, "<img src='$2' alt='$1'>");

  // LINKS
  md = md.replace(/\[(.*?)\]\((.*?)\)/gim, "<a href='$2'>$1</a>");

  // TABLES
  md = md.replace(
    /\|(.+)\|\n\|([-\s|:]+)\|\n((\|.*\|\n?)*)/g,
    (match, header, sep, body) => {
      const headers = header
        .split("|")
        .map((h) => h.trim())
        .filter(Boolean);

      let html = ["<table><thead><tr>"];

      headers.forEach((h) => html.push(`<th>${h}</th>`));

      html.push("</tr></thead><tbody>");

      body
        .trim()
        .split("\n")
        .forEach((row) => {
          const cols = row
            .split("|")
            .map((c) => c.trim())
            .filter(Boolean);

          html.push("<tr>");
          cols.forEach((c) => html.push(`<td>${c}</td>`));
          html.push("</tr>");
        });

      html.push("</tbody></table>");

      return html.join("");
    },
  );

  // LIST PARSER
  const lines = md.split("\n");
  const html = [];

  let inUL = false;
  let inOL = false;

  for (let line of lines) {
    // TASK LIST
    if (/^- \[ \] /.test(line)) {
      if (!inUL) {
        html.push("<ul class='task-list'>");
        inUL = true;
      }
      html.push(
        `<li><input type="checkbox" disabled> ${line.replace(/^- \[ \] /, "")}</li>`,
      );
      continue;
    }

    if (/^- \[x\] /.test(line)) {
      if (!inUL) {
        html.push("<ul class='task-list'>");
        inUL = true;
      }
      html.push(
        `<li><input type="checkbox" checked disabled> ${line.replace(/^- \[x\] /, "")}</li>`,
      );
      continue;
    }

    // ORDERED LIST
    if (/^\d+\.\s+/.test(line)) {
      if (!inOL) {
        html.push("<ol>");
        inOL = true;
      }
      html.push(`<li>${line.replace(/^\d+\.\s+/, "")}</li>`);
      continue;
    }

    // UNORDERED LIST
    if (/^- /.test(line)) {
      if (!inUL) {
        html.push("<ul>");
        inUL = true;
      }
      html.push(`<li>${line.replace(/^- /, "")}</li>`);
      continue;
    }

    // CLOSE LISTS
    if (inUL) {
      html.push("</ul>");
      inUL = false;
    }

    if (inOL) {
      html.push("</ol>");
      inOL = false;
    }

    html.push(line + "<br>");
  }

  if (inUL) html.push("</ul>");
  if (inOL) html.push("</ol>");

  preview.innerHTML = html.join("");
}

const components = {
  h1: "# Heading 1",
  h2: "## Heading 2",
  h3: "### Heading 3",
  bold: "**Bold Text**",
  italic: "*Italic Text*",
  highlight: "==Highlight Text==",
  strikethrough: "~~Strikethrough Text~~",
  blockquote: "> Blockquote",
  subscript: "H~2~O",
  superscript: "E=mc^2",
  hr: "---",
  ol: "1. First item\n2. Second item\n3. Third item",
  ul: "- First item\n- Second item\n- Third item",
  tasklist: "- [ ] Task 1\n- [x] Task 2\n- [ ] Task 3",
  code: "`Code`",
  codeblock: "```\nCode block\n```",
  link: "[title](https://www.example.com)",
  image:
    "![alt text](https://www.mamp.one/wp-content/uploads/2024/09/image-resources2.jpg)",
  table:
    "| Header 1 | Header 2 |\n| --- | --- |\n| Cell 1 | Cell 2 |\n| Cell 3 | Cell 4 |",
};

function add_component(id) {
  const textarea = document.getElementById("markdown-input");

  let value = textarea.value;
  const start = textarea.selectionStart;
  const end = textarea.selectionEnd;

  const insertText = components[id];

  // Insert at cursor position
  textarea.value =
    value.substring(0, start) + insertText + value.substring(end);

  // Move cursor after inserted text
  const newCursorPos = start + insertText.length;
  textarea.selectionStart = textarea.selectionEnd = newCursorPos;

  // Update hidden fields
  content1.value = textarea.value;
  content2.value = textarea.value;

  // Focus back to textarea
  textarea.focus();

  // Re-render preview
  parse_markdown();
}

function download_markdown() {
  const textarea = document.getElementById("markdown-input");

  if (!textarea) return;

  const markdown = textarea.value || "";

  const blob = new Blob([markdown], { type: "text/markdown;charset=utf-8;" });

  const url = URL.createObjectURL(blob);

  const a = document.createElement("a");
  a.href = url;
  a.download = "file_name.md";
  a.style.display = "none";

  document.body.appendChild(a);
  a.click();

  document.body.removeChild(a);
  URL.revokeObjectURL(url);
}

function upload_markdown() {
  const fileInput = document.createElement("input");

  fileInput.type = "file";
  fileInput.accept = ".md,text/markdown";

  fileInput.onchange = function (event) {
    const file = event.target.files[0];

    if (!file) return;

    const reader = new FileReader();

    reader.onload = function (e) {
      const content = e.target.result;

      const textarea = document.getElementById("markdown-input");
      const content1 = document.getElementById("content1");
      const content2 = document.getElementById("content2");

      textarea.value = content;
      content1.value = content;
      content2.value = content;

      parse_markdown();
    };

    reader.readAsText(file);
  };

  fileInput.click();
}
