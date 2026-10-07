# Module 4 Learning Notes

## Stage 1 - Understanding My Existing Project

### Existing Program Flow

#### Function that reads the CSV

Function Name:
`read_students_csv()`

Purpose:
Reads student data from a CSV file and returns valid student records.

---

#### Function that rejects invalid rows

Function Name:
`validate_student_row()`

Purpose:
Checks each row and rejects data with missing names, non-numeric marks, or marks outside the allowed range.

---

#### Function that calculates results

Function Name:
`calculate_summary()`

Purpose:
Calculates:

- Total valid students
- Total invalid rows
- Pass count
- Fail count
- Average marks
- Highest score

---

#### Function that displays results

Function Name:
`display_results()`

Purpose:
Displays the calculated results in the terminal.

---

#### How main() connects everything

Program Flow:

1. `main()` starts execution.
2. The CSV file is loaded using `read_students_csv()`.
3. Invalid rows are rejected during validation.
4. Valid student data is passed to `calculate_summary()`.
5. The calculated summary is displayed using `display_results()`.
6. The program finishes.

---

### Trace Exercise: Student With Marks 82.5

Example CSV row:

```csv
Cara,82.5
```

1. The value `82.5` is first read from the CSV as text.
2. During validation, the value is converted using:

```python
float("82.5")
```

3. After conversion, the value becomes the float:

```python
82.5
```

4. The numeric value is then used to:
   - Determine Pass/Fail status
   - Calculate averages
   - Compare highest scores
   - Generate reports

---

# Stage 2 - Predictions Before Running

## Sample Data

```csv
name,marks
Asha,39
Ben,40
Cara,82.5
Noor,abc
,70
Zoya,105
```

---

## Prediction 1: Accepted Rows

I predict the following rows will be accepted:

- Asha (39)
- Ben (40)
- Cara (82.5)

---

## Prediction 2: Rejected Rows

I predict the following rows will be rejected:

| Row | Reason |
|------|---------|
| Noor,abc | Marks are not numeric |
| ,70 | Missing student name |
| Zoya,105 | Marks are greater than 100 |

---

## Prediction 3: Pass Count With Threshold 40

Passing students:

- Ben
- Cara

Predicted pass count:

```text
2
```

---

## Prediction 4: Pass Count With Threshold 50

Passing students:

- Cara

Predicted pass count:

```text
1
```

---

## Prediction 5: Average and Highest Score

Calculation:

```text
(39 + 40 + 82.5) / 3
= 53.83
```

Predicted average:

```text
53.83
```

Predicted highest score:

```text
Cara - 82.5
```

---

## Actual Results

(To be completed after running the program.)

### Threshold 40

Result:

```text
[Paste actual output here]
```

Comparison with prediction:

```text
[Write observations here]
```

---

### Threshold 50

Result:

```text
[Paste actual output here]
```

Comparison with prediction:

```text
[Write observations here]
```

---

## Corrections and Learning

If any predictions were incorrect, record them here.

Example:

- I initially predicted ...
- The actual result was ...
- I learned that ...