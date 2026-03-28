// 1. Define the asynchronous function to fetch and process the JSON data
async function fetchJsonData(url) {
  try {
    // Fetch the data from the specified URL
    const response = await fetch(url);
    //console.log(response)

    // Check if the request was successful
    if (!response.ok) {
      throw new Error(`HTTP error! Status: ${response.status}`);
    }

    // Parse the response as JSON (this returns a JavaScript object)
    const data = await response.json();

    // Process the data here (e.g., update the DOM, run calculations)
    //console.log("Data fetched:", data);
    return data;
    updateUI(data); // Call a function to handle your logic
  } catch (error) {
    console.error("Error fetching or processing JSON:", error);
  }
}

// 2. Define a function to use the fetched data
function updateUI(data) {
  updateSummary(data);
  updateAvail(data);
  updateGroups(data);
  updatePass(data);
}

function updateSummary(data) {
  const summaryElement = document.getElementById("summary"); //get parent of summary cards
  const summ_data = data[0];
  const summChildren = summaryElement.children; //list of all the cards

  const summOrder = [
    "Remaining Arrivals",
    "Stay Overs",
    "Currently In House",
    "Remaining Departures",
    "Departed Guests",
    "Vacant Dirty",
    "Arriving Tomorrow",
    "Out of Order",
    "Vacant Clean",
  ];
  //edit values and labels for summary cards
  for (let i = 0; i < summChildren.length; i++) {
    const summValue = summChildren[i].children[0].children[0]; //get Value element
    const summLabel = summChildren[i].children[0].children[1]; //get Label element
    // console.log(summLabel, summValue,  summ_data[i]["label"], summ_data[i]["value"]);

    const dataIndex = summ_data.findIndex(
      (name) => name.label === summOrder[i],
    );
    // console.log(summ_data[dataIndex]["label"]);
    summLabel.textContent = summ_data[dataIndex]["label"];
    summValue.textContent = summ_data[dataIndex]["value"];
    // console.log(summLabel, summValue);
  }
}

function updateAvail(data) {
  const availElement = document.getElementById("avail"); //get parent of availability cards
  const availData = data[1];
  const availChildren = availElement.children; //list of all the cards
  //edit values and labels for availability cards
  for (let i = 0; i < availData.length && i < 4; i++) {
    const availCount = availChildren[i].children[0].children[0]; //get count element
    const availRoom = availChildren[i].children[0].children[1]; //get room type element
    const availPrice = availChildren[i].children[0].children[2]; //get price element
    const availChange = availChildren[i].children[0].children[3]; //get price change element

    // console.log(availCount, availRoom,  availPrice[i]["label"], summ_data[i]["value"]);

    availCount.textContent = availData[i]["count"];
    availRoom.textContent = availData[i]["room"];

    // let currPrice = parseFloat(availData[i]["price"].replace("$ ", ""));
    let availDiffFloat = parseFloat(availData[i]["diff"].replace("$", ""));
    // const pairs = [
    //   [0, 2],
    //   [1, 3],
    // ];
    // // let getPairIndex = pairs.find((pair) => pair.includes(i));
    // let getPairIndex = pairs
    //   .find((pair) => pair.includes(i))
    //   .find((ind) => ind !== i);
    // console.log(i, getPairIndex);
    // if (currPrice == 0) {
    //   oldPrice = parseFloat(availData[i]["old price"].replace("$ ", ""));
    //   pairPrice = parseFloat(availData[getPairIndex]["price"].replace("$ ", ""));
    //   if (pairPrice > 0) {
    //     availData[i]["price"] = availData[getPairIndex]["price"];
    //     availData[i]["diff"] = availData[getPairIndex]["diff"];
    //     availDiffFloat = parseFloat(availData[i]["diff"].replace("$", ""));
    //     console.log("reached1");
    //   } else {
    //     availData[i]["price"] = availData[i]["old price"];
    //   }
    // } else if (availDiffFloat == 0) {
    //   availData[i]["diff"] = availData[getPairIndex]["diff"];
    //   availDiffFloat = parseFloat(availData[i]["diff"].replace("$", ""));
    //   console.log("reached2");
    // }
    availPrice.textContent = availData[i]["price"];

    if (availDiffFloat > 0) {
      availChange.innerHTML = "&uarr; " + availData[i]["diff"];
      availChange.classList.replace("bg-secondary", "bg-success");
    } else if (availDiffFloat < 0) {
      availChange.innerHTML = "&darr; " + availData[i]["diff"];
      availChange.classList.replace("bg-secondary", "bg-danger");
    } else {
      availChange.textContent = availData[i]["diff"];
    }

    // console.log(summLabel, summValue);
  }
}

function updateGroups(data) {
  const groupElement = document.getElementById("groups"); //get parent of summary cards
  const groupData = data[2];
  const groupChildren = groupElement.children; //list of all the cards

  //edit values and labels for summary cards
  for (let i = 0; i < groupData.length && i < 4; i++) {
    j = i + 1; //normally skip first row for header but if more than 3 groups, use all 4 rows
    if (groupData.length > 3) {
      j = i;
    }

    const groupName = groupChildren[j].children[0]; //get count element
    const groupArr = groupChildren[j].children[1]; //get Label element
    const groupDep = groupChildren[j].children[2];
    const groupBlock = groupChildren[j].children[3];
    const groupPick = groupChildren[j].children[4];
    // console.log(groupCount, groupRoom,  groupPrice[i]["label"], summ_data[i]["value"]);

    groupArr.textContent = groupData[i]["Arrival"];
    groupBlock.textContent = groupData[i]["Blocked"];
    groupDep.textContent = groupData[i]["Departure"];
    groupPick.textContent = groupData[i]["Picked Up"];
    groupName.textContent = groupData[i]["Reservation Name"];
    // console.log(summLabel, summValue);
  }
}

function updatePass(data) {
  let passElement1 = document.getElementById("pass1"); //get parent of summary cards
  let passElement2 = document.getElementById("pass2");
  const passData = data[3];
  let passCard = passElement1.children[0];

  //create cards based on how many pass down logs and enter values
  for (let i = 0; passData.length > i && i < 6; i++) {
    if (i == 3) {
      const clone = passCard.cloneNode(true);
      passElement2.appendChild(clone);
      passCard = clone;
    } else if (i != 0) {
      const clone = passCard.cloneNode(true);
      passCard.after(clone);
      passCard = clone;
    }
    // console.log(i, "reached", passCard);
    const passTitle = passCard.children[0].children[0];
    const passTime = passCard.children[0].children[1];
    const passMess = passCard.children[1];

    passTime.textContent =
      "(" + passData[i]["timestamp"].replace(".0", "") + ")";
    passTitle.textContent = passData[i]["title"];
    passMess.textContent = passData[i]["message"];
  }

  //create another column of 3 rows if more than 3 logs
  if (passData.length > 3) {
    passElement2.parentElement.hidden = false;
    passElement1.parentElement.classList.replace("col-12", "col-6");
  } else {
    passElement1.parentElement.classList.replace("col-6", "col-12");
    // console.log(passCard);
  }
}

function setRefreshInterval(intervalTimeSec) {
  const refreshElement = document.getElementById("refresh");
  // console.log(intervalTimeSec);
  refreshElement.setAttribute("content", intervalTimeSec);
}


async function init() {
  const config = await fetchJsonData("/config/HTML_config.json");
  //console.log(config["dataFile"])
  const dashboardData = await fetchJsonData(config["dataFile"]);

  setRefreshInterval(config["HTMLrefreshIntervalseconds"]);
  updateUI(dashboardData);
}

// Call the fetch function immediately on page load
//fetchJsonData(jsonUrl);
init();

// Optional: To stop the continuous calls, you can use clearInterval(intervalId);
