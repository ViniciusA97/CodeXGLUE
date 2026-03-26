// Fixed: Correct date comparison
public boolean isBefore(Date date1, Date date2) {
    return date1.getTime() < date2.getTime();
}
