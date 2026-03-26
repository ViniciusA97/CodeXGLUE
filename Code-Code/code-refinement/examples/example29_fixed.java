// Fixed: Added bounds check
public int getElement(int[] array, int index) {
    if (index < 0 || index >= array.length) return -1;
    return array[index];
}
