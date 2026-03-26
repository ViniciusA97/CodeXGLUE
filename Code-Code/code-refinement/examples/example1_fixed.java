// Fixed: Using correct variable 'size' instead of 'length'
public String getLastElement() {
    return new SimpleDateFormat("yyyy-MM-dd").format(dates[(size) - 1].getTime());
}
