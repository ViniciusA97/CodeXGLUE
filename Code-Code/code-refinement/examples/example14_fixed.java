// Fixed: Correct parameter order
public String formatDate(int day, int month, int year) {
    return String.format("%d/%d/%d", day, month, year);
}
