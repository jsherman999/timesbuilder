const RSS_URL = "https://rss.nytimes.com/services/xml/rss/nyt/HomePage.xml";
const MEDIA_NAMESPACE = "http://search.yahoo.com/mrss/";

const status = document.querySelector("#status");
const grid = document.querySelector("#article-grid");
const articleCount = document.querySelector("#article-count");

function textFrom(parent, selector) {
  return parent.querySelector(selector)?.textContent.trim() || "";
}

function imageFrom(item) {
  const media = [...item.getElementsByTagNameNS(MEDIA_NAMESPACE, "content")]
    .map((node) => ({
      url: node.getAttribute("url"),
      width: Number(node.getAttribute("width")) || 0,
    }))
    .filter((image) => image.url)
    .sort((a, b) => b.width - a.width);

  if (media[0]) return media[0].url;

  const thumbnail = item.getElementsByTagNameNS(MEDIA_NAMESPACE, "thumbnail")[0];
  return thumbnail?.getAttribute("url") || "";
}

function archiveUrl(nytUrl) {
  return `https://archive.ph/${nytUrl}`;
}

function appendText(element, text) {
  if (text) element.append(document.createTextNode(text));
}

function renderArticle(article, index) {
  const card = document.createElement("article");
  card.className = `card${index < 2 ? " hero" : ""}`;

  const link = document.createElement("a");
  link.className = "card-link";
  link.href = archiveUrl(article.url);
  link.target = "_blank";
  link.rel = "noopener noreferrer";

  if (article.imageUrl) {
    const image = document.createElement("img");
    image.className = "card-img";
    image.src = article.imageUrl;
    image.alt = "";
    image.loading = "lazy";
    link.append(image);
  }

  const title = document.createElement("h2");
  title.className = "card-title";
  appendText(title, article.title);
  link.append(title);

  if (article.summary) {
    const summary = document.createElement("p");
    summary.className = "card-summary";
    appendText(summary, article.summary);
    link.append(summary);
  }

  const meta = document.createElement("div");
  meta.className = "card-meta";

  const badge = document.createElement("span");
  badge.className = "badge";
  badge.textContent = "archive.ph";
  meta.append(badge);

  const original = document.createElement("a");
  original.className = "orig";
  original.href = article.url;
  original.target = "_blank";
  original.rel = "noopener noreferrer";
  original.textContent = "NYT original ›";
  meta.append(original);

  card.append(link, meta);
  return card;
}

function parseArticles(xml) {
  const channel = xml.querySelector("channel");
  if (!channel) throw new Error("The NYT feed did not contain a channel.");

  const articles = [...channel.querySelectorAll("item")]
    .map((item) => ({
      title: textFrom(item, "title"),
      url: textFrom(item, "link"),
      summary: textFrom(item, "description").replace(/\s+/g, " "),
      imageUrl: imageFrom(item),
    }))
    .filter((article) => article.title && article.url);

  if (!articles.length) throw new Error("The NYT feed did not contain any articles.");
  return { articles, updatedAt: textFrom(channel, "lastBuildDate") };
}

async function loadPage() {
  const response = await fetch(`${RSS_URL}?timesbuilder=${Date.now()}`, {
    cache: "no-store",
  });
  if (!response.ok) throw new Error(`The NYT feed returned HTTP ${response.status}.`);

  const xml = new DOMParser().parseFromString(await response.text(), "application/xml");
  if (xml.querySelector("parsererror")) throw new Error("The NYT feed was not valid XML.");
  return parseArticles(xml);
}

loadPage()
  .then(({ articles, updatedAt }) => {
    grid.replaceChildren(...articles.map(renderArticle));
    status.textContent = `Homepage rebuilt with archive.ph links · updated ${updatedAt || "just now"}`;
    articleCount.textContent = `${articles.length} articles from the NYT HomePage RSS feed.`;
  })
  .catch((error) => {
    console.error(error);
    status.textContent = "Could not load the current NYT HomePage.";
    grid.replaceChildren();
    const message = document.createElement("p");
    message.className = "loading error";
    message.textContent = "The live NYT feed could not be loaded. Please refresh and try again.";
    grid.append(message);
    articleCount.textContent = "No articles loaded.";
  });
