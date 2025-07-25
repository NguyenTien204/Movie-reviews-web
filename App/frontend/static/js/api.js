async function registerUser(userData) {
  const response = await fetch(`${AUTH_URL}/register`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData)
  });

  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || "Registration failed");
  return result; // result = { access_token, token_type }
}

// Example:


async function loginUser(userData) {
  const response = await fetch(`${AUTH_URL}/login`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(userData)
  });

  const result = await response.json();
  if (!response.ok) throw new Error(result.detail || "Login failed");
  return result;
}

// Example:

async function getTrendingMovies() {
  const response = await fetch(`${BASE_URL}/movies/trending`);
  return await response.json();
}

async function getMovieTrailers(movieId) {
  const response = await fetch(`${BASE_URL}/movies/${movieId}/trailer`);
  return await response.json();
}

async function getMovieRecommendations(movieId) {
  const response = await fetch(`${BASE_URL}/movies/${movieId}/recommendations`);
  return await response.json();
}


async function getMovieDetail(movieId) {
  const response = await fetch(`${BASE_URL}/movies/${movieId}`);
  const data = await response.json();
  return data;
}


async function getMovieShortDetail(movieId) {
  const response = await fetch(`${BASE_URL}/shortdetail/${movieId}`);
  return await response.json();
}

async function filterMovies(params) {
  const query = new URLSearchParams(params).toString();
  const response = await fetch(`${BASE_URL}/movies/filter?${query}`);
  return await response.json();
}


document.addEventListener("DOMContentLoaded", () => {
  const movieId = window.location.pathname.split("/").pop();

  fetch(`${BASE_URL}/movies/12`)
    .then(response => {
      if (!response.ok) {
        throw new Error("Failed to fetch movie details");
      }
      return response.json();
    })
    .then(data => {
      const jsonContainer = document.getElementById("json-output");
      jsonContainer.textContent = JSON.stringify(data, null, 2); 
    })
    .catch(error => {
      console.error("Error:", error);
      document.getElementById("json-output").textContent = "Lỗi khi lấy dữ liệu.";
    });
});
