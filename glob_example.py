def glob_match(pattern: str, string: str) -> bool:
    p_idx, s_idx = 0, 0
    p_star_idx = -1
    s_backtrack_idx = -1
    
    p_len = len(pattern)
    s_len = len(string)

    while s_idx < s_len:
        # Case 1: Elements match, or pattern has a single-character wildcard '?'
        if p_idx < p_len and (pattern[p_idx] == string[s_idx] or pattern[p_idx] == '?'):
            p_idx += 1
            s_idx += 1
            
        # Case 2: We hit an asterisk '*'. 
        # Mark this position so we can backtrack here if the match fails later.
        elif p_idx < p_len and pattern[p_idx] == '*':
            p_star_idx = p_idx
            s_backtrack_idx = s_idx
            p_idx += 1 # Move past the '*' in the pattern
            
        # Case 3: Current characters don't match, but we passed a '*' earlier.
        # Backtrack: assume the '*' consumes this mismatching character and try again.
        elif p_star_idx != -1:
            p_idx = p_star_idx + 1
            s_backtrack_idx += 1
            s_idx = s_backtrack_idx
            
        # Case 4: Complete mismatch with no wildcards to save us
        else:
            return False

    # Clean up trailing asterisks in the pattern (e.g., matching "king" against "king***")
    while p_idx < p_len and pattern[p_idx] == '*':
        p_idx += 1

    # If we consumed the entire pattern, it's a perfect match!
    return p_idx == p_len

if __name__ == "__main__":
    print(glob_match("*right", "left right"))
    print(glob_match("*right", "left right (outher text)"))
    breakpoint()
