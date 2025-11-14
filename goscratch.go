package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

func main() {
	// Create a temporary file
	tmpFile, err := os.CreateTemp("", "example-*.txt")
	if err != nil {
		fmt.Println("Error creating temp file:", err)
		return
	}
	defer os.Remove(tmpFile.Name()) // Clean up

	// Write some data to the temporary file
	data := []byte("Hello, World!")
	if _, err := tmpFile.Write(data); err != nil {
		fmt.Println("Error writing to temp file:", err)
		return
	}

	// Prompt the user for input
	fmt.Print("Enter some text: ")
	reader := bufio.NewReader(os.Stdin)
	input, err := reader.ReadString('\n')
	if err != nil {
		fmt.Println("Error reading input:", err)
		return
	}

	// Write user input to the temporary file
	_, err = tmpFile.WriteString(strings.TrimSpace(input))
	if err != nil {
		fmt.Println("Error writing to temp file:", err)
		return
	}

	// Close the file
	if err := tmpFile.Close(); err != nil {
		fmt.Println("Error closing temp file:", err)
		return
	}

	// Read the data back from the temporary file
	readData, err := os.ReadFile(tmpFile.Name())
	if err != nil {
		fmt.Println("Error reading temp file:", err)
		return
	}

	// Print the data read from the file
	fmt.Println("Data read from temp file:", string(readData))
}
