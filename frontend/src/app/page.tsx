"use client";

import { useState } from "react";
import styles from "./page.module.css"
import {
  Box,
  Button,
  CircularProgress,
  FormControl,
  InputLabel,
  MenuItem,
  Select,
  styled,
  Typography
} from "@mui/material";
import { SelectChangeEvent } from "@mui/material/Select";
import CloudUploadIcon from "@mui/icons-material/CloudUpload";

export default function Home() {
  const [mode, set_mode] = useState("");
  const [image_file, set_image_file] = useState<File | null>(null);
  const [image_url, set_image_url] = useState<string | null>(null);
  const [encrypted_image_url, set_encrypted_image_url] = useState<string | null>(null);
  const [is_loading, set_is_loading] = useState(false);

  const handle_click = async () => {
    if (!image_file || !mode) {
      return;
    }

    set_is_loading(true);

    var form_data = new FormData();
    form_data.append("image", image_file);
    form_data.append("mode", mode);

    fetch("http://localhost:5000/encrypt", {
      method: "POST",
      body: form_data,
      redirect: "follow"
    })
      .then(response => response.blob())
      .then(blob => {
        const encrypted_image_url = URL.createObjectURL(blob);
        set_encrypted_image_url(encrypted_image_url);
      })
      .catch(error => console.log("error", error))
      .finally(() => set_is_loading(false));
  };

  return (
    <Box className={styles.main} component="main">
      <Typography
        variant="h2"
        component="h1"
        className={styles.title}
      >
        Image Encryption With DES
      </Typography>

      <Box className={styles.main_content}>
        <Box className={styles.left_hand_side}>
          {image_url ? (
            <Box className={styles.image_wrapper}>
              <img
                src={image_url}
                alt="Uploaded Image"
                className={styles.image}
              />
            </Box>
          ) : (
            <InputFileUpload
              set_image_file={set_image_file}
              set_image_url={set_image_url}
            />
          )}
        </Box>


        <Box className={styles.right_hand_side}>
          <Box className={styles.image_wrapper}>
            {encrypted_image_url &&
              <img
                src={encrypted_image_url}
                alt={"Encrypted Image"}
                className={styles.image}
              />
            }
          </Box>
        </Box>
      </Box>

      <Box className={styles.user_options_wrapper}>
        <Box className={styles.user_options}>
          <ModeSelect
            mode={mode}
            set_mode={set_mode}
          />

          <Button
            disabled={!(mode !== "" && image_file) || is_loading}
            fullWidth
            onClick={handle_click}
            variant="contained"
          >
            {is_loading ? <CircularProgress /> : "Encrypt"}
          </Button>
        </Box>
      </Box>
    </Box>
  )
}

type ModeSelectProps = {
  mode: string,
  set_mode: (mode: string) => void
}

function ModeSelect(props: ModeSelectProps) {
  function handle_select(event: SelectChangeEvent) {
    props.set_mode(event.target.value as string);
  };

  return (
    <Box
      sx={{
        width: "25%"
      }}
    >
      <FormControl fullWidth>
        <InputLabel id="mode">Mode</InputLabel>
        <Select
          labelId="mode"
          id="mode-select"
          value={props.mode}
          label="Mode"
          onChange={handle_select}
        >
          <MenuItem value={"ECB"}>ECB</MenuItem>
          <MenuItem value={"CBC"}>CBC</MenuItem>
          <MenuItem value={"CFB"}>CFB</MenuItem>
          <MenuItem value={"OFB"}>OFB</MenuItem>
          <MenuItem value={"CTR"}>CTR</MenuItem>
        </Select>
      </FormControl>
    </Box>
  );
}

const VisuallyHiddenInput = styled("input")({
  clip: "rect(0 0 0 0)",
  clipPath: "inset(50%)",
  height: 1,
  overflow: "hidden",
  position: "absolute",
  bottom: 0,
  left: 0,
  whiteSpace: "nowrap",
  width: 1,
});

type InputFileUploadProps = {
  set_image_file: (file: File | null) => void,
  set_image_url: (url: string | null) => void
}

function InputFileUpload(props: InputFileUploadProps) {
  function handle_file_upload(event: React.ChangeEvent<HTMLInputElement>) {
    const file = event.target.files ? event.target.files[0] : null;

    if (!file || !file.type.startsWith("image/")) {
      return;
    }

    props.set_image_file(file);

    const reader = new FileReader();
    reader.addEventListener("loadend", (event) => {
      props.set_image_url(reader.result as string);
    });
    reader.readAsDataURL(file); // Fires the "loadend" event when finished reading file
  };

  return (
    <Button
      className={styles.upload_image_button}
      component="label"
      fullWidth
      variant="outlined"
      startIcon={<CloudUploadIcon />}
    >
      Upload Image
      <VisuallyHiddenInput
        onChange={handle_file_upload}
        type="file"
        accept="image/png"
      />
    </Button>
  );
}

