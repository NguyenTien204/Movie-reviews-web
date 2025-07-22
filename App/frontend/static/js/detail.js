document.addEventListener("DOMContentLoaded", () => {
  const modal = document.getElementById("reviewModal");
  const editLink = document.querySelector(".post-myreview a");
  const closeBtn = document.querySelector(".close-btn");

  // Bấm vào link "Edit My Review" → mở modal
  editLink.addEventListener("click", function (event) {
    event.preventDefault(); // Ngăn chuyển trang
    modal.style.display = "block";
  });

  // Bấm vào nút dấu X → đóng modal
  closeBtn.addEventListener("click", function () {
    modal.style.display = "none";
  });

  // Bấm ra ngoài modal → cũng đóng
  window.addEventListener("click", function (event) {
    if (event.target === modal) {
      modal.style.display = "none";
    }
  });
});
