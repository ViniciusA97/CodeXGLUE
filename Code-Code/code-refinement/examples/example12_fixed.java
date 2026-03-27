public String reverseString(String input) {
    if (input == null) {
        return null;
    }
    StringBuilder result = new StringBuilder();
    for (int i = input.length() - 1; i >= 0; i--) {
        result.append(input.charAt(i));
    }
    return result.toString();
}
