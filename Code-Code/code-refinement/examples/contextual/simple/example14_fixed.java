public int getLastElement(int[] array) {
    if (array == null || array.length == 0) {
        return -1;
    }
    return array[array.length - 1];
}
