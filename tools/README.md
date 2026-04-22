diff --git a/README.md b/README.md
index 6de755db8a7094befb64c526890c105e86751086..e0a7e824126185cdfb3e698d394309f1684abd3c 100644
--- a/README.md
+++ b/README.md
@@ -20,25 +20,54 @@ favorite image viewer and delete possible duplicates. This often happens
 when the video jumps back and forth between slides.
 
 You can then combine the slides to a pdf with a tool like convert:
 
     convert `ls -v outprefix*.png` outprefix.pdf
 
 
 Dependencies
 ------------
 
 * opencv 4.x
 
 
 Build Instructions
 ------------------
 
     make
     make install # DESTDIR= PREFIX=/usr/local
 
 
 License
 -------
 
 BSD 2-Clause license, see LICENSE for more details.
 
+
+Resume builder helper
+---------------------
+
+This repository now includes a small CLI helper to generate a role-tailored
+resume draft from structured JSON input:
+
+    python3 tools/resume_builder.py --input examples/resume_input_template.json --output resume.md
+
+What it does:
+
+* Builds ATS-friendly one-column markdown output that is ready to export as PDF.
+* Flags missing information needed for stronger impact bullets.
+* Checks for required setup context (target role/JD, experience summary,
+  career level, and special context).
+* Adds a short `Changes made` section explaining key edits.
+
+Notes:
+
+* The tool does not fabricate achievements or metrics.
+* You should tailor every generated draft to a specific job description.
+
+WordPress + Elementor installation
+----------------------------------
+
+If you want to run this resume builder from a WordPress site that uses Elementor,
+see the integration guide:
+
+* `docs/wordpress-elementor-install.md`
