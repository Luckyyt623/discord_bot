fetch("https://slither-realtime-leaderboard.pages.dev/api/leaderboard")
  .then(res => res.json())
  .then(data => {
    const container = document.getElementById("servers");
    data.dataList.forEach(server => {
      const card = document.createElement("div");
      card.className = "server-card";

      const header = document.createElement("div");
      header.className = "server-header";
      header.innerText = `Server: ${server.ipv4}:${server.po} | Snakes: ${server.snakeCount}`;
      card.appendChild(header);

      server.leaderboard?.slice(0, 5).forEach(p => {
        const div = document.createElement("div");
        div.className = "player";
        div.innerHTML = `<span>${p.place}. ${p.nk}</span><span>Score: ${p.len}</span>`;
        card.appendChild(div);
      });

      container.appendChild(card);
    });
  })
  .catch(err => {
    document.getElementById("servers").innerText = "Failed to load leaderboard data.";
    console.error(err);
  });