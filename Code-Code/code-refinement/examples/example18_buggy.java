// Bug: Resource leak - file not closed
public String readFile(String path) throws IOException {
    BufferedReader reader = new BufferedReader(new FileReader(path));
    return reader.readLine();
}
