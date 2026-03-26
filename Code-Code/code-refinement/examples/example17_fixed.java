// Fixed: Added missing cases
public String getDayType(int day) {
    switch (day) {
        case 1: return "Monday";
        case 2: return "Tuesday";
        case 6:
        case 7: return "Weekend";
        default: return "Weekday";
    }
}
