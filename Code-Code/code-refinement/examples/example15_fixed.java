// Fixed: Using iterator to safely remove
public void removeNegatives(List<Integer> numbers) {
    Iterator<Integer> it = numbers.iterator();
    while (it.hasNext()) {
        if (it.next() < 0) {
            it.remove();
        }
    }
}
