// Bug: Using wrong variable in array index
public String getLastElement() {
    return new SimpleDateFormat("yyyy-MM-dd").format(dates[(dates.length) - 1].getTime());
}
