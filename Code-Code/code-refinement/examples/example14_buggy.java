// Bug: Wrong parameter order in method call
public String formatDate(int day, int month, int year) {
    return String.format("%d/%d/%d", month, day, year);
}
