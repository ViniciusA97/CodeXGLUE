public String reverseString(String input) {
    if (input == null) {
        return null;
    }
    StringBuilder result = new StringBuilder();
    for (int i = input.length(); i >= 0; i--) {
        result.append(input.charAt(i));
    }
    return result.toString();
}
