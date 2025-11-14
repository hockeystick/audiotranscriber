# Transcript Output Format Examples

This document shows examples of the improved, copy-paste friendly transcript formats.

## Non-Diarized Transcripts (Standard Format)

### Previous Format
```
This is the first sentence this is the second sentence this is the third sentence
```

### New Format
```
This is the first sentence.

This is the second sentence.

This is the third sentence.
```

**Benefits:**
- Proper paragraph breaks after sentences
- Easy to read and copy-paste
- Natural document flow

---

## Diarized Transcripts (With Speaker Identification)

### Previous Format (Word-by-Word)
```
Speaker 1: Hello how are you doing today
Speaker 2: I'm fine thanks how about you
Speaker 1: I'm good let's get started
```

### New Format (With Timestamps - When Available)
```
[00:12] Speaker 1: Hello, how are you doing today?

[00:18] Speaker 2: I'm fine, thanks. How about you?

[00:24] Speaker 1: I'm good. Let's get started with the presentation.
```

### New Format (Without Timestamps)
```
Speaker 1: Hello, how are you doing today?

Speaker 2: I'm fine, thanks. How about you?

Speaker 1: I'm good. Let's get started with the presentation.
```

**Benefits:**
- Complete thoughts grouped together per speaker
- Clear visual separation between speakers
- Optional timestamps show when each speaker started
- Professional format suitable for meeting notes, interviews, podcasts
- Easy to copy directly into documents, emails, or notes

---

## Multi-Chunk Transcripts

When large files are split into chunks, they're combined with clear separators:

### Diarized Multi-Chunk Format
```
Speaker 1: This is the content from the first chunk of audio.

Speaker 2: Response from the first chunk.

==================================================

Speaker 1: This is the content from the second chunk.

Speaker 2: Response from the second chunk.
```

### Standard Multi-Chunk Format
```
This is the content from the first chunk of audio.

This is the content from the second chunk of audio.
```

**Benefits:**
- Clear visual boundaries between chunks
- Maintains context while showing file segments
- Easy to identify chunk boundaries if needed

---

## Usage Tips

1. **For Meeting Minutes**: Copy-paste diarized format directly into your notes
2. **For Transcription Services**: Professional format ready for clients
3. **For Content Creation**: Extract quotes easily with proper attribution
4. **For Accessibility**: Screen readers handle the formatted text better
5. **For Documentation**: Natural paragraph structure for archival

## Format Features

✅ **Copy-Paste Friendly**: No cleanup needed after copying
✅ **Professional Layout**: Suitable for business documents
✅ **Speaker Clarity**: Easy to identify who said what
✅ **Timestamp Support**: Optional time references
✅ **Paragraph Breaks**: Natural reading flow
✅ **Clean Separators**: Clear chunk boundaries

---

## Technical Details

### Google Cloud Provider (Chirp 3)
- Groups consecutive words from same speaker
- Adds timestamps from word-level timing data when available
- Double line breaks between speaker turns
- Handles missing word-level data gracefully

### OpenAI Provider
- Cleans whitespace from output
- Filters empty transcripts in chunked mode
- Consistent paragraph formatting
- (Note: Diarization currently disabled due to SDK stability)

### Automatic Formatting
All formatting is applied automatically by the providers. No user configuration needed!
