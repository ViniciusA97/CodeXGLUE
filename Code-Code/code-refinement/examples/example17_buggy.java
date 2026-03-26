// Bug: Missing break in switch case
public String getDayType(int day) {
    switch (day) {
        case 1: return "Monday";
        case 2: return "Tuesday";
        default: return "Weekend";
    }
}
