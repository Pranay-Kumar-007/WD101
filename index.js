let form = document.getElementById("pp");

let getEntries = () => {
  let entries = localStorage.getItem("userEntry");

  if (entries) {
    entries = JSON.parse(entries);
  } else {
    entries = [];
  }
  return entries;
};

let Entries = getEntries();

let showEntries = () => {
  let entries = getEntries();

  let rows = entries
    .map((entry) => {
      let name = `<td class="td">${entry.name}</td>`;
      let email = `<td class="td">${entry.email}</td>`;
      let password = `<td class="td">${entry.password}</td>`;
      let dob = `<td class="td">${entry.dob}</td>`;
      let acceptConditions = `<td class="td">${entry.acceptConditions}</td>`;

      let row = `<tr>${name} ${email} ${password} ${dob} ${acceptConditions}</tr>`;
      return row;
    })
    .join("\n");

  let tableDiv = document.getElementById("tt1");

  tableDiv.innerHTML = `<table class="table" border="1">
  <tr>
    <th class="th">Name</th>
    <th class="th">Email</th>
    <th class="th">Password</th>
    <th class="th">Dob</th>
    <th class="th">Accepted terms?</th>
  </tr>
    ${rows}
  </table>`;
};

let saveUserFrom = (event) => {
  event.preventDefault();

  let name = document.getElementById("name").value;
  let email = document.getElementById("email").value;
  let password = document.getElementById("password").value;
  let dob = document.getElementById("dob").value;
  let acceptConditions = document.getElementById("agree").checked;

  let entry_obj = {
    name,
    email,
    password,
    dob,
    acceptConditions,
  };

  Entries.push(entry_obj);

  localStorage.setItem("userEntry", JSON.stringify(Entries));

  showEntries();
};

form.addEventListener("submit", saveUserFrom);

showEntries();

let getAge = (today, birthDate) => {
  let age = today.getFullYear() - birthDate.getFullYear();
  let m = today.getMonth() - birthDate.getMonth();
  if (m < 0 || (m === 0 && today.getDate() < birthDate.getDate())) {
    age--;
  }
  return age;
};

let dateELE = document.getElementById("dob");

dateELE.addEventListener("change", () => {
  let [date, month, year] = document.getElementById("dob").value.split("-");

  let dob = new Date(date, month, year);
  let Today = new Date();

  age = getAge(Today, dob);

  dateELE.style.border = "2px solid rgba(0, 0, 0, 0.4)";
  if (age < 18 || age > 55) {
    dateELE.setCustomValidity("Age should be between 18 and 55.");
    dateELE.style.border = "2px solid red";
    return;
  } else {
    dateELE.setCustomValidity("");
  }
});

let email = document.getElementById("email");

email.addEventListener("input", () => validate(email));

let validate = (alk) => {
  if (alk.validity.typeMismatch) {
    alk.setCustomValidity("Enter correct Email ID!");
    alk.reportValidity();
  } else {
    alk.setCustomValidity("");
  }
};