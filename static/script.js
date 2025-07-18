document.addEventListener("DOMContentLoaded", () => {
    const calendarBtn = document.getElementById("calendarBtn");
    const calendarModal = document.getElementById("calendarModal");
    const closeBtn = document.querySelector(".close");
    const calendarDiv = document.getElementById("calendar");

    calendarBtn.addEventListener("click", () => {
        calendarModal.style.display = "block";
        loadCalendar();
    });

    closeBtn.addEventListener("click", () => {
        calendarModal.style.display = "none";
    });

    window.onclick = function(event) {
        if (event.target === calendarModal) {
            calendarModal.style.display = "none";
        }
    };

    // 💗 Load calendar with marked entry dates
    function loadCalendar() {
        fetch("/entry-dates")
            .then(response => response.json())
            .then(dates => {
                calendarDiv.innerHTML = "";
                const today = new Date();
                const year = today.getFullYear();
                const month = today.getMonth();
                const daysInMonth = new Date(year, month + 1, 0).getDate();

                for (let day = 1; day <= daysInMonth; day++) {
                    const dateStr = `${year}-${String(month + 1).padStart(2, '0')}-${String(day).padStart(2, '0')}`;
                    const dayDiv = document.createElement("div");
                    dayDiv.classList.add("calendar-day");
                    if (dates.includes(dateStr)) {
                        dayDiv.classList.add("marked"); // 💗
                    }
                    dayDiv.textContent = day;
                    calendarDiv.appendChild(dayDiv);
                }
            });
    }
});
