const apiUrl = "http://127.0.0.1:8000/properties/";

async function fetchProperties() {
    const response = await fetch(apiUrl);
    const data = await response.json();
    const propertiesDiv = document.getElementById("properties");

    if (data.properties.length === 0) {
        propertiesDiv.innerHTML = "<p>No properties available.</p>";
        return;
    }

    data.properties.forEach(property => {
        const propertyElement = document.createElement("div");
        propertyElement.innerHTML = `
            <h2>${property.title}</h2>
            <p>${property.description}</p>
            <p><strong>Price:</strong> $${property.price}</p>
            <p><strong>Location:</strong> ${property.location}</p>
            ${property.image ? `<img src="${property.image}" alt="${property.title}">` : ""}
        `;
        propertiesDiv.appendChild(propertyElement);
    });
}

fetchProperties();

function updateMenu() {
    const sessionToken = localStorage.getItem("sessionToken");
    const nav = document.querySelector("header nav ul");

    nav.querySelectorAll("li").forEach(item => {
        if (["Profile", "Logout", "Login"].includes(item.textContent.trim())) {
            item.remove();
        }
    });

    if (sessionToken) {
        const profileItem = document.createElement("li");
        const profileLink = document.createElement("a");
        profileLink.href = "profile.html";
        profileLink.innerText = "Profile";
        profileItem.appendChild(profileLink);
        nav.appendChild(profileItem);

        const logoutItem = document.createElement("li");
        const logoutLink = document.createElement("a");
        logoutLink.href = "#";
        logoutLink.innerText = "Logout";
        logoutLink.addEventListener("click", () => {
            localStorage.removeItem("sessionToken");
            alert("You have been logged out.");
            location.reload();
        });
        logoutItem.appendChild(logoutLink);
        nav.appendChild(logoutItem);
    } else {
        const loginItem = document.createElement("li");
        const loginLink = document.createElement("a");
        loginLink.href = "login.html";
        loginLink.innerText = "Login";
        loginItem.appendChild(loginLink);
        nav.appendChild(loginItem);
    }
}

updateMenu();