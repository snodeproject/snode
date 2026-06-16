console.log("MSW file");

function orpiedi(weekDays = "l, ma, me, g, v, s, d") {
    let returner;

    if (weekDays === "l, ma, me, g, v, s, d") {
        returner = "DefaultOrpiedi";
    } else {
        returner =
            weekDays
                .replaceAll(" ", "")
                .replaceAll(",", ":orpiedi.car.next:")
            + ".ORPIEDI";
    }

    return returner;
}