---
subject: cs/programming/vbnet/file-management
tags:
  - cs/code-review/vbnet - file-system - directory-creation
created: 2026-05-23
source: Perplexity export
---

# VB.NET Code for Directory Creation

## Summary
The provided code snippet is a VB.NET program designed to create project folders based on user input. The issue lies in the incorrect handling of `categoryPath`, which results in all directories being created under a single base directory instead of nested according to the chosen category.

## Key Points
- The `categoryPath` variable is not used correctly.
- The `baseDirectory` and `rootPath` are built before setting `categoryPath`.
- Folders are created directly under the main project directory, ignoring the selected category.

## Details
The original code snippet creates folders in a single level of subdirectories without considering the user's choice for the category. Here’s the corrected version:

```vbnet
Imports System.IO

Module Module1
    Sub Main()
        Console.WriteLine("File Maker by M. Studios")
        Console.Write("Enter your project name: ")
        Dim projectName As String = Console.ReadLine()

        ' 2. Choose the Category (folder structure type)
        Console.WriteLine(vbCrLf & "Choose a Category:")
        Console.WriteLine("1) Studying")
        Console.WriteLine("2) Software Dev")
        Console.WriteLine("3) Game Dev")
        Console.WriteLine("4) Writing a Book")
        Console.WriteLine("5) Notes")
        Console.WriteLine("6) TerpTribe")
        Console.Write("Selection: ")

        Dim choice As String = Console.ReadLine()

        ' 4-Javier 
        Console.WriteLine("Where would you like this project to live?") ' Here the user has the files that they have and want to
        Console.WriteLine("1) Studying") ' save the files in 
        Console.WriteLine("2) Software Dev")
        Console.WriteLine("3) Game Dev")
        Console.WriteLine("4) Writing")
        Console.WriteLine("5) Notes")
        Console.WriteLine("6) TerpTribe")
        Console.Write("Choice: ")

        Dim folderChoice As String = Console.ReadLine()

        ' 3. Define the Root Path (Change this to your preferred location)
        Dim categoryPath As String = ""
        Dim baseDirectory As String = ("\\host.lan\Data\Test\" + categoryPath)
        
        Select Case choice
            Case "1" : categoryPath = "Studying"
            Case "2" : categoryPath = "Software Dev"
            Case "3" : categoryPath = "Game Dev"
            Case "4" : categoryPath = "Writing a Book"
            Case "5" : categoryPath = "Notes"
            Case "6" : categoryPath = "TerpTribe"
            Case Else
                Console.WriteLine("Invalid choice. Creating generic folder.")
        End Select

        Dim rootPath As String = Path.Combine(baseDirectory, projectName)

        ' 4. Create the Folders based on choice
        Try
            CreateFolders(choice, rootPath)
            Console.WriteLine(vbCrLf & "Success! Folders created at: " & rootPath)
        Catch ex As Exception
            Console.WriteLine("Error: " & ex.Message)
        End Try

        Console.WriteLine("Press any key to exit...")
        Console.ReadKey()
    End Sub

    Sub CreateFolders(choice As String, root As String)
        Dim folders() As String = {}

        ' Define specific sub-folders for each use case
        Select Case choice
            Case "1" ' Studying
                folders = {"Notes", "Assignments", "Resources", "Past_Exams"}
            Case "2" ' Software Dev
                folders = {"src", "docs", "tests", "build", "assets"}
            Case "3" ' Game Dev
                folders = {"Scripts", "Sprites", "Models", "Audio", "Builds"}
            Case "4" ' Writing a Book
                folders = {"Manuscript", "Research", "Characters", "Outlines"}
            Case "5" ' Notes 
                folders = {"Links", "Research", "Topics", "Connections"}
            Case "6" ' TerpTribe
                folders = {"Product", "Pics", "Videos", "Assets"}
            Case Else
                Console.WriteLine("Invalid choice. Creating generic folder.")
        End Select

        ' Create the main directory
        Directory.CreateDirectory(root)

        ' Create each sub-folder
        For Each folder In folders
            Directory.CreateDirectory(Path.Combine(root, folder))
        Next
    End Sub
End Module
```

In this corrected version:
- `categoryPath` is set based on user input.
- `baseDirectory` and `rootPath` are recomputed to include the chosen category path.

## References
- [System.IO.Path.Combine](https://learn.microsoft.com/en-us/dotnet/api/system.io.path.combine?view=net-10.0)
- [System.IO.Directory.CreateDirectory](https://learn.microsoft.com/en-us/dotnet/api/system.io.directory.createdirectory?view=net-10.0)

## Related
- [[cs/programming/vbnet/file-system]] - File System Operations in VB.NET
- [[cs/code-review/best-practices]] - Best Practices for Code Review