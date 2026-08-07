# Acronym decision table

400 acronyms, 135,907 occurrences, from a full
scan of 712,881 files. Fill in **YOUR_ACTION** and **YOUR_SPOKEN** in
`docs/acronyms-table.tsv` (same rows, tab-separated) and hand it back.

`suggested_action` is a starting point only — it was derived from patterns,
not from reading every context. Override freely.

| action | meaning |
|---|---|
| `SPELL` | say it letter by letter |
| `EXPAND` | replace with the full Vietnamese phrase (put it in YOUR_SPOKEN) |
| `LOWERCASE` | not an acronym — an ordinary word in a shouty header |
| `STRIP` | reasoning-scaffolding leakage; remove, never speak |
| `KEEP` | leave exactly as-is for the model |

---

### AI — 67,322× — suggested: `SPELL`
- *Chào Anh, tôi là Meddies, một trợ lý AI được thiết kế để giúp anh trình bày rõ ràng các vấn đề sức khỏe của mình.*
- *Tôi là Meddies, trợ lý AI chuyên hỗ trợ tư vấn sức khỏe và thu thập thông tin y khoa.*
- *Chào em, tôi là Meddies, trợ lý AI chuyên tư vấn sức khỏe.*

### MRI — 6,860× — suggested: `SPELL`
- *được: - Thăm khám trực tiếp, test vận động - Bác sĩ sẽ quyết định có cần chụp X-quang hay MRI không - X-quang giúp xem xương và khe khớp, MRI đánh giá sụn, gân, **Tại sao không nên*
- *sĩ sẽ quyết định có cần chụp X-quang hay MRI không - X-quang giúp xem xương và khe khớp, MRI đánh giá sụn, gân, **Tại sao không nên tự ý đoán bệnh?** - Vì triệu chứng của chị có th*
- ***Đi khám bác sĩ chuyên khoa cơ xương khớp** để chụp MRI hoặc siêu âm, xác định chính xác nguyên nhân.*

### ECG — 2,970× — suggested: `SPELL`
- *sẽ cần làm một số xét nghiệm để loại trừ các nguyên nhân nguy hiểm như: - **Điện tâm đồ (ECG)**: Kiểm tra nhịp tim và hoạt động điện.*
- *Các xét nghiệm thường làm khi khám tim mạch:** - **Điện tâm đồ (ECG)**: Ghi lại hoạt động điện của tim - **Siêu âm tim**: Xem cấu trúc và chức năng tim - **Xét nghiệm máu**: Đán*
- *ể làm thêm một số xét nghiệm như: - Xét nghiệm máu (để kiểm tra thiếu máu) - Điện tâm đồ (ECG) để xem nhịp tim - Siêu âm tim nếu cần Mai Anh nên đi khám sớm để yên tâm nhé!*

### CCCD — 2,677× — suggested: `EXPAND` → `căn cước công dân`
- *Khi đi khám, bác chỉ cần: - Mang theo CCCD hoặc giấy tờ tùy thân để đăng ký khám - Nhớ mang theo thẻ bảo hiểm y tế nếu có - Ghi lại các triệu chứng bác*
- ***Chuẩn bị trước khi đi khám**: - Mang theo CMND/CCCD và tiền mặt.*
- *Về khám chuyên khoa:** - **Chuẩn bị**: Anh chỉ cần mang theo CCCD và bảo hiểm y tế.*

### BHYT — 2,482× — suggested: `EXPAND` → `bảo hiểm y tế`
- *m máu cơ bản sẽ hợp lý hơn nhiều so với phòng khám tư nhân, và nếu em có **Bảo hiểm y tế (BHYT)** thì sẽ được chi trả một phần hoặc toàn bộ tùy tuyến khám.*
- ***Giấy tờ cần mang theo**: - Thẻ Bảo hiểm y tế (BHYT).*
- *- Tiền mặt (để đóng tiền nếu có xét nghiệm ngoài BHYT).*

### CMND — 2,462× — suggested: `EXPAND` → `chứng minh nhân dân`
- ***Chuẩn bị trước khi đi khám**: - Mang theo CMND/CCCD và tiền mặt.*
- ***Về vật dụng:** - Không cần mang gì đặc biệt ngoài: - CMND/Thẻ bảo hiểm y tế (nếu có) - Danh sách thuốc đang dùng (nếu có, dù bác nói không uống thuốc thường xuyên) - G*
- ***Chuẩn bị hồ sơ**: - Mang theo CMND/Thẻ bảo hiểm y tế.*

### CT — 2,299× — suggested: `SPELL`
- *g gan thận - **Siêu âm hạch**: Đánh giá kích thước, cấu trúc hạch (dịch hay đặc) - **Chụp CT hoặc PET-CT**: Nếu hạch to hoặc nghi ngờ ác tính - **Sinh thiết hạch**: Nếu cần thiết đ*
- ***Siêu âm hạch**: Đánh giá kích thước, cấu trúc hạch (dịch hay đặc) - **Chụp CT hoặc PET-CT**: Nếu hạch to hoặc nghi ngờ ác tính - **Sinh thiết hạch**: Nếu cần thiết để xác định ch*
- *ắn hạch kỹ lưỡng và có thể chỉ định: - Xét nghiệm máu (CBC, CRP, VSR) - Chụp X-quang hoặc CT scan nếu cần - Sinh thiết hạch nếu nghi ngờ 2.*

### TV — 2,036× — suggested: `SPELL`
- *từ từ duỗi thẳng một chân ra, giữ 5-10 giây - Lặp lại 10 lần mỗi bên - Có thể làm khi xem TV hoặc ngồi nghỉ **Bài tập 3: Đi bộ nhẹ nhàng** - Đi bộ 15-20 phút mỗi ngày, nơi bằng phẳ*
- *, bác nên: - Uống ít nước hơn vào buổi tối để không phải dậy đi vệ sinh nhiều - Tránh xem TV hoặc điện thoại trước khi ngủ 30 phút - Giữ phòng ngủ mát mẻ, yên tĩnh **Lưu ý quan trọ*
- *- **Giường chỉ để ngủ**: Tránh làm việc, xem TV hay dùng điện thoại trên giường.*

### FIFE — 1,975× — suggested: `STRIP`
- *- FIFE: Khó ăn uống, ngại vệ sinh.*
- *Đã khai thác đủ OPQRST, Red Flags, PMH, Medications, Social History, ROS, và FIFE.*
- *internal_reasoning **Giai đoạn**: Gathering Information (Phase 2) - Hoàn thành khai thác FIFE và Red Flags.*

### NGAY — 1,879× — suggested: `LOWERCASE` → `ngay`
- *KHI NÀO CẦN DỪNG TẬP VÀ ĐI KHÁM NGAY?** Nếu trong hoặc sau khi tập mà anh thấy: - Đầu gối sưng to, nóng, đỏ, hoặc sốt.*
- *Nếu cơn đau **hết trong 5-10 phút** khi nghỉ → không sao, tiếp tục theo dõi - **ĐI CẤC CỨ NGAY** nếu: - Đau dữ dội, không giảm khi nghỉ - Đau kéo dài **quá 15-20 phút** - Đau kèm **
- *TỪ NGAY BÂY GIỜ:** - **Tiếp tục uống thuốc đều đặn** Metformin và Amlodipine như đang dùng (không tự ý ngưng) - **Kiể*

### B12 — 1,556× — suggested: `SPELL`
- *Nhưng trước tiên, anh có biết gì về tình trạng thiếu vitamin B12 không?*
- *Nếu chưa, tôi sẽ chia sẻ thêm: Vitamin B12 rất quan trọng cho thần kinh và máu.*
- *Thiếu B12 thường do ăn uống không đủ chất, đặc biệt là người ít ăn thịt, cá, hoặc ăn nhiều đồ chiên rán.*

### GERD — 1,526× — suggested: `SPELL`
- *- Differentials: Có thể do trào ngược dạ dày thực quản (GERD), tác dụng phụ thuốc (dù Amlodipine ít), hoặc do thay đổi huyết áp/thần kinh ban đêm.*
- *- **Đau rát sau xương ức**: Có thể do trào ngược acid (GERD) hoặc viêm thực quản, hoặc cũng có thể là triệu chứng tim mạch.*
- ***Đau rát sau xương ức** có thể do trào ngược acid (GERD) - hay gặp ở người cao tuổi.*

### TSH — 1,434× — suggested: `SPELL`
- *ssibility* of autoimmune conditions and the need for specific blood tests (CBC, Cortisol, TSH, Antibodies).*
- *Advise on blood tests (Cortisol, TSH, CBC, Antibodies).*
- *- **TSH, Free T4** (để kiểm tra tuyến giáp).*

### QUAN — 1,357× — suggested: `LOWERCASE` → `quan`
- ***NHẮN NHỦ QUAN TRỌNG**: - Tất cả thông tin trên là chung chung, không phải đơn thuốc - Anh PHẢI đi khám bác sĩ để được chẩn*
- *...) - Thuốc đang dùng: __ - Tiếp xúc nguồn lây: __ (vật nuôi, người bệnh...) --- **LƯU Ý QUAN TRỌNG**: - Gọi điện cho bệnh viện trước để xác nhận quy trình đăng ký - Mang theo tất*
- *oặc oil-free - Thoa khi da còn ẩm nhẹ để khóa nước **Bước 3: Kem chống nắng (Sunscreen) - QUAN TRỌNG NHẤT** - Đây là bước chống lão hóa tốt nhất --- **II.*

### SPF — 1,225× — suggested: `SPELL`
- *Dù làm văn phòng, anh vẫn nên dùng kem chống nắng SPF 30+ mỗi sáng.*
- *care routine cụ thể:** **Bước 1: Chống nắng (bắt buộc)** - Anh nên dùng kem chống nắng có SPF 30-50, broad spectrum (chống cả UVA và UVB).*
- *thêm về cách chọn sản phẩm an toàn: **Nguyên tắc chọn sản phẩm:** - **Chống nắng**: Chọn SPF 30-50, ghi "broad spectrum", "non-comedogenic" (không gây bít lỗ chân lông).*

### T4 — 1,012× — suggested: `SPELL`
- *- **TSH, Free T4** (để kiểm tra tuyến giáp).*
- ***Tuyến giáp:** TSH, Free T4.*
- *Anh cần đến bệnh viện xét nghiệm **Cortisol, ACTH, TSH, Free T4** để chẩn đoán chính xác.*

### BHA — 913× — suggested: `SPELL`
- *m Sóc Tăng Cường (Tối - Tuần 2-3 lần)** - **Tẩy tế bào chết nhẹ**: Dùng sản phẩm chứa AHA/BHA 1-2 lần/tuần để loại bỏ da cũ, giúp da sáng hơn.*
- ***Không dùng chung**: Tránh dùng Retinol chung với Vitamin C hay AHA/BHA trong cùng buổi tối lúc mới bắt đầu.*
- *- Da em còn trẻ, không cần dùng hoạt chất mạnh như Retinol hay AHA/BHA cao.*

### UV — 750× — suggested: `SPELL`
- *độ tuổi của bác, nếp nhăn và da khô là do quá trình lão hóa tự nhiên và tác động của tia UV.*
- *Tia UV là nguyên nhân hàng đầu gây nếp nhăn - **Rửa mặt nhẹ nhàng**: Nên dùng sữa rửa mặt dịu nhẹ thay vì chỉ nước t*
- *ng của quá trình lão hóa tự nhiên (tuổi 48), cộng với tác động của ánh nắng mặt trời (tia UV) mà không có biện pháp bảo vệ, cùng với stress và tình trạng da khô.*

### BPPV — 742× — suggested: `SPELL`
- ***Anh có biết gì về chứng chóng mặt tư thế (BPPV) hoặc rối loạn tiền đình không?** **Tôi xin chia sẻ một số khả năng**: Triệu chứng của anh rất giống với tình*
- *ẻ một số khả năng**: Triệu chứng của anh rất giống với tình trạng rối loạn tiền đình hoặc BPPV, có thể do sự thay đổi dịch trong tai trong hoặc ảnh hưởng của tư thế ngồi lái xe lâu*
- *rõ ràng**: "Đặc biệt là khi đứng dậy" → Rất gợi ý **chóng mặt tư thế kịch phát lành tính (BPPV)** hoặc **huyết áp thấp tư thế**.*

### LEGO — 729× — suggested: `SPELL`
- *Con cũng muốn được vẽ tranh và chơi LEGO như bình thường ạ.*
- *Con không sốt, chỉ đau ở đầu gối thôi, và con rất muốn được chạy nhảy, vẽ tranh, chơi LEGO như bình thường.*
- *- Đau nhiều hơn - Không đi được Chúc con mau hết đau để được chạy nhảy, vẽ tranh và chơi LEGO với các bạn nhé!*

### COPD — 722× — suggested: `SPELL`
- *- Hô hấp: Hen suyễn, COPD, tràn dịch màng phổi...*
- ***Trước giờ bác có biết về suy tim hay bệnh phổi tắc nghẽn mạn tính (COPD) không ạ?** Nếu bác chưa rõ, tôi xin giải thích ngắn gọn: Huyết áp cao kéo dài có thể làm tim phải làm việ*
- *Càng lâu càng nghĩ đến mạn tính như suy tim, COPD).*

### IBS — 721× — suggested: `SPELL`
- ***Hội chứng ruột kích thích (IBS):** Đây là tình trạng ruột bị nhạy cảm quá mức, thường gây đau bụng, táo bón hoặc tiêu chảy.*
- *Tôi sẽ chia sẻ thẳng thắn: **Về nguy hiểm và điều trị:** - **Hội chứng ruột kích thích (IBS)**: Không nguy hiểm đến tính mạng, không gây ung thư, và có thể kiểm soát được bằng thay*
- *Nhiều người sống chung với IBS rất tốt nếu biết cách quản lý.*

### AN — 697× — suggested: `LOWERCASE` → `an`
- *dưỡng ẩm cả mặt (nhiều hơn vùng má) - Điều chỉnh thói quen nhíu mày, ngủ đủ giấc **LƯU Ý AN TOÀN**: Nếu anh áp dụng đều đặn 4-6 tuần mà tình trạng nếp nhăn, khô ráp không cải thiện*
- ***Nếu KHÔNG dùng retinol**: Dùng kem dưỡng ẩm bình thường **LƯU Ý AN TOÀN**: - **Luôn patch test** (thử trên tay trước) 1-2 ngày trước khi dùng trên mặt - **Chỉ thêm 1 sản phẩm m*
- *ôn dùng kem chống nắng SPF 30-50 - ✅ Theo dõi da và ngưng nếu có kích ứng nặng **NHẮC NHỞ AN TOÀN**: - Nếu da có bất kỳ dấu hiệu nguy hiểm nào (đỏ rát, bong mảng lớn, ngứa dữ dội) *

### KHI — 624× — suggested: `LOWERCASE` → `khi`
- *KHI NÀO CẦN DỪNG TẬP VÀ ĐI KHÁM NGAY?** Nếu trong hoặc sau khi tập mà anh thấy: - Đầu gối sưng to, nóng, đỏ, hoặc*
- ***LƯU Ý KHI TẬP:** - Tập từ từ, không vội vàng.*
- *KHI CƠN ĐAU XUẤT HIỆN:** - **Ngay lập tức ngưng hoạt động**, ngồi xuống nghỉ ngơi - Nếu cơn đau **hết trong 5-10*

### CRP — 623× — suggested: `SPELL`
- *Các xét nghiệm cần thiết có thể bao gồm**: - Xét nghiệm máu tổng quát, CRP - Xét nghiệm lao (nếu cần) - Siêu âm hạch để đánh giá đặc điểm **3.*
- *ư sau: **Các xét nghiệm thường cần**: - **Xét nghiệm máu**: Đếm tế bào máu, markers viêm (CRP, procalcitonin), chức năng gan thận - **Siêu âm hạch**: Đánh giá kích thước, cấu trúc *
- *ĩ sẽ thăm khám trực tiếp, sờ nắn hạch kỹ lưỡng và có thể chỉ định: - Xét nghiệm máu (CBC, CRP, VSR) - Chụp X-quang hoặc CT scan nếu cần - Sinh thiết hạch nếu nghi ngờ 2.*

### NGUY — 595× — suggested: `LOWERCASE` → `nguy`
- *Theo em, em muốn chọn lựa chọn nào?** Trước khi em quyết định, tôi cần chia sẻ **dấu hiệu NGUY HIỂM** cần đưa bé đến bệnh viện ngay lập tức: - Sốt cao trên 39°C - Khó thở, thở nhan*
- *ổi tối - Có thể dùng "retinol sandwich": kem dưỡng ẩm → retinol → kem dưỡng ẩm **DẤU HIỆU NGUY HIỂM (cần NGƯNG NGAY):** 🛑 **Da đỏ rát, nóng ran** như cháy nắng 🛑 **Bong tróc thành *
- *ng bụng - Mệt mỏi, chán ăn - Tuổi 73, chỉ có tiền sử cao huyết áp **Đây là những dấu hiệu NGUY HIỂM có thể chỉ ung thư đại trực tràng, polyp lớn, hoặc bệnh lý nghiêm trọng khác.** *

### IVF — 589× — suggested: `SPELL`
- *- **Thụ tinh nhân tạo (IVF):** Nếu lạc nội mạc nặng, IVF là giải pháp hiệu quả cao.*
- ***Sự khác biệt giữa IUI và IVF:** **IUI (Intrauterine Insemination):** - Bác sĩ sẽ bơm tinh trùng đã được rửa sạch trực tiếp vào tử cung vào*
- *o một chu kỳ) - Phù hợp khi còn một ít tinh trùng tốt và buồng trứng vẫn có thể đáp ứng **IVF (In Vitro Fertilization):** - Thu lấy trứng và tinh trùng, thụ tinh trong phòng lab, s*

### PHASE — 578× — suggested: `STRIP`
- *Phase: GATHERING INFORMATION (Turn 5) - Moving to PHASE 3: PROVIDING STRUCTURE Patient Age: 62 Objective: Summarize findings, provide education using Ask-Tell-Ask me*
- *<think> **Kiểm tra giai đoạn**: Tôi đang ở PHASE 4 (CLOSING).*
- ***PHASE 3: PROVIDING STRUCTURE** Trước tiên, Tôi muốn xác nhận: việc gia đình chuẩn bị chuyển bé lên Bệnh viện Ung bư*

### T3 — 537× — suggested: `SPELL`
- *hiếu máu, nhiễm trùng - Đường huyết: loại trừ đái tháo đường - Chức năng tuyến giáp (TSH, T3, T4): kiểm tra rối loạn tuyến giáp - Các chỉ số viêm: CRP, tốc độ máu lắng **2.*
- *máu (kiểm tra thiếu máu), đường huyết, chức năng gan thận, và xét nghiệm tuyến giáp (TSH, T3, T4) để loại trừ suy giáp.*
- *sẽ chỉ định làm xét nghiệm máu để kiểm tra nồng độ hormone tuyến giáp (TSH, Free T4, Free T3).*

### OPQRST — 526× — suggested: `STRIP`
- *Đã khai thác đủ OPQRST, Red Flags, PMH, Medications, Social History, ROS, và FIFE.*
- ***Phân tích**: - Đã hoàn thành khai thác OPQRST, Red Flags, FIFE.*
- *- Cần khai thác thêm OPQRST cho các triệu chứng này, đặc biệt là thời gian xuất hiện và mức độ.*

### EMG — 524× — suggested: `SPELL`
- *bác sĩ chuyên khoa thần kinh hoặc cơ xương khớp để được chẩn đoán chính xác bằng điện cơ (EMG) nếu cần.*
- *không đỡ, Anh nên đi khám để bác sĩ đánh giá chính xác mức độ chèn ép (có thể cần điện cơ EMG) và có phác đồ điều trị phù hợp hơn.*
- *n kinh**: Để kiểm tra chính xác tổn thương thần kinh, có thể làm thêm xét nghiệm điện cơ (EMG) nếu cần - **Hoặc Khám Cơ xương khớp**: Nếu nghi ngờ vấn đề cột sống cổ là nguyên nhân*

### BV — 517× — suggested: `EXPAND` → `bệnh viện`
- ***Ưu tiên hàng đầu**: Ho tất cả thủ tục để bé được nhập viện sớm tại BV Ung bướu Hà Nội 2.*
- *Điều trị triệt để vẫn phải là phẫu thuật và hóa trị theo phác đồ tại BV Ung bướu Hà Nội.*
- *Hoàn tất thủ tục chuyển bé lên BV Ung bướu Hà Nội sớm nhất có thể 2.*

### CBC — 514× — suggested: `SPELL`
- *Bác sĩ sẽ thăm khám trực tiếp, sờ nắn hạch kỹ lưỡng và có thể chỉ định: - Xét nghiệm máu (CBC, CRP, VSR) - Chụp X-quang hoặc CT scan nếu cần - Sinh thiết hạch nếu nghi ngờ 2.*
- *Xét nghiệm máu cơ bản (không đau, chi phí ~200-400k):** - **CBC (máu toàn bộ)**: lấy máu ở ngón tay hoặc tĩnh mạch, rất nhanh - **CRP, VSR**: đánh giá viêm nhiễm - **Thời gi*
- *Xét nghiệm máu**: - Đếm tế bào máu (CBC) để xem có nhiễm trùng không - Xét nghiệm viêm (CRP, tốc độ máu lắng) - Chức năng gan, thận - Xét nghiệm các*

### HPV — 513× — suggested: `SPELL`
- *Tuy nhiên, **tiêm vắc-xin HPV** là rất quan trọng để phòng ngừa ung thư cổ tử cung, ngay cả ở độ tuổi của bác nếu bác vẫn còn quan hệ tình*
- *- Mang theo **hồ sơ tiêm chủng** (nếu có) để hỏi về vắc-xin HPV.*
- *Hỏi bác sĩ về việc tiêm vắc-xin HPV nếu bác chưa tiêm.*

### HP — 500× — suggested: `SPELL`
- *sát trực tiếp niêm mạc, xem có viêm loét hay không, và có thể sinh thiết nếu cần - **Test HP**: Kiểm tra vi khuẩn Helicobacter pylori nếu nghi ngờ - Các xét nghiệm khác tùy tình tr*
- ***Xét nghiệm phân**: Tìm ký sinh trùng, máu ẩn, vi khuẩn HP (nếu nghi ngờ dạ dày).*
- *àng tốt để được chẩn đoán chính xác (có thể là trào ngược, viêm loét, hoặc nhiễm vi khuẩn HP).*

### CHO — 486× — suggested: `LOWERCASE` → `cho`
- *VỀ KEM CHỐNG NẮNG CHO DA DẦU** **Loại phù hợp**: - Chọn kem chống nắng vật lý lai hóa học hoặc hóa học - Dạng lotion/kem mỏng, oil-*
- *CÁCH DÙNG KEM DƯỠNG ẨM CHO DA HỖN HỢP** Anh nên **thoa cả mặt**, nhưng điều chỉnh lượng: - **Vùng chữ T (trán, mũi, cằm)**: Thoa một lớp*
- *ge trên da khô - **Bước 2**: Rửa lại bằng sữa rửa mặt dịu nhẹ --- **TÓM LẠI QUY TRÌNH TỐI CHO ANH**: 1.*

### HTN — 442× — suggested: `SPELL`
- *- Tiền sử: HTN, DM, BPH.*
- *Tiền sử **Cao huyết áp (HTN)**, đang dùng thuốc đều.*
- *- **PMH**: Cao huyết áp (HTN).*

### AMH — 398× — suggested: `SPELL`
- *AMH thấp*
- *(Ví dụ: giải thích rõ hơn về AMH, hay tư vấn cách cải thiện?)*
- *Tôi muốn hiểu rõ hơn về chỉ số AMH này, nó có ảnh hưởng gì đến việc có con không, và có cách nào cải thiện được không.*

### NSAID — 397× — suggested: `SPELL`
- *Thuốc giảm đau Ibuprofen (thuộc nhóm NSAID) có thể làm tăng huyết áp và giảm tác dụng của một số loại thuốc điều trị cao huyết áp.*
- ***Giảm đau nhanh**: Thuốc chống viêm đặc hiệu (colchicine, NSAID) giúp giảm đau rất nhanh, nhưng **tôi không thể kê đơn được**.*
- *Cung cấp thông tin về thuốc giảm đau (colchicine/NSAID) 2.*

### BMI — 391× — suggested: `SPELL`
- *Với chiều cao 1m58 và cân nặng 62kg, chỉ số BMI của anh/chị khoảng 24.8 - đây là mức cân nặng bình thường, không phải nguyên nhân chính gây ra vấn đề này.*
- *(Để tính chỉ số BMI) Thông tin này sẽ giúp tôi có cái nhìn tổng quan hơn về tình trạng sức khỏe của anh.*
- *Với cân nặng 62kg và chiều cao 1m60, chỉ số BMI của anh là 24.2, vẫn trong mức bình thường.*

### PMH — 390× — suggested: `STRIP`
- *- PMH: Sạch.*
- *Đã khai thác đủ OPQRST, Red Flags, PMH, Medications, Social History, ROS, và FIFE.*
- ***Tiền sử bệnh lý (PMH)**: Cháu có bệnh nền gì không (tiểu đường, tim mạch...)?*

### ROS — 390× — suggested: `STRIP`
- *- ROS: Hôi miệng (+), không chảy máu nướu, há miệng bình thường.*
- *Đã khai thác đủ OPQRST, Red Flags, PMH, Medications, Social History, ROS, và FIFE.*
- *n thành phần **FIFE** (Feelings, Ideas, Function, Expectations) và **Review of Systems** (ROS) liên quan đến cơ xương khớp.*

### LDL — 371× — suggested: `SPELL`
- ***Lipidogram**: Kiểm tra lại cholesterol (tổng cholesterol, LDL, HDL) để đánh giá chính xác tình trạng của em.*
- *evolocumab, alirocumab) hoặc Inclisiran - đây là những thuốc mới, tiêm dưới da, giúp giảm LDL cholesterol rất hiệu quả.*
- *(ví dụ: LDL bao nhiêu, cholesterol toàn phần bao nhiêu?).*

### RA — 369× — suggested: `LOWERCASE` → `ra`
- *phút thường gợi ý viêm xương khớp (OA), trong khi > 30-60 phút gợi ý viêm khớp dạng thấp (RA) hoặc các bệnh viêm khớp khác.*
- *Khả năng **Viêm khớp dạng thấp (RA)** thấp hơn nhưng không loại trừ hoàn toàn (do có cứng khớp buổi sáng và đau đối xứng), nhưng RA thường có tr*
- *hấp hơn nhưng không loại trừ hoàn toàn (do có cứng khớp buổi sáng và đau đối xứng), nhưng RA thường có triệu chứng toàn thân hơn.*

### UTI — 338× — suggested: `SPELL`
- *l:** medical evaluation I need to ask about specific symptoms to differentialiate between UTI stones stones, etc..*
- *i, triệu chứng kéo dài 3-4 ngày), đây có thể là dấu hiệu của nhiễm trùng đường tiết niệu (UTI) - một tình trạng khá phổ biến ở nữ giới.*
- *Tuy nhiên, dựa trên những gì anh mô tả, tôi có thể chia sẻ những điều sau: **Anh có biết UTI (nhiễm trùng đường tiểu) hay sỏi thận không?** Những triệu chứng anh đang có - đau lưng*

### G6PD — 338× — suggested: `SPELL`
- ***Tán huyết cấp**: Có thể do thuốc, miễn dịch, di truyền (G6PD, spherocytosis).*
- *Thiếu men G6PD*
- ***Về vấn đề G6PD:** Thiếu men G6PD là một bệnh di truyền, người bệnh cần tránh một số loại thuốc và thực phẩm nhất định.*

### N95 — 310× — suggested: `SPELL`
- *Về môi trường làm việc:** - Kiểm tra lại chất lượng khẩu trang (nên dùng loại N95 hoặc có van thở).*
- *của anh**: - Theo dõi tại nhà với nước muối súc họng, uống nhiều nước ấm - Đeo khẩu trang N95 khi làm việc trong bếp - Chế độ ăn mềm, mát, tránh cay nóng - Cải thiện thông gió bếp *
- *Anh nên dùng khẩu trang N95 hoặc khẩu trang có van thở, loại chuyên dụng cho môi trường có khói dầu.*

### FSH — 307× — suggested: `SPELL`
- *- **Xét nghiệm hormone sinh dục nam** (như Testosterone, FSH, LH) để kiểm tra xem có sự mất cân bằng nội tiết tố nào không.*
- *số lượng, chất lượng tinh trùng - **Xét nghiệm máu**: Kiểm tra hormone (testosterone, LH, FSH), đường huyết, chức năng thận gan - **Siêu âm**: Siêu âm tuyến tiền liệt, tinh hoàn để*
- *Xét nghiệm nội tiết tố máu**: - **FSH, LH**: Đánh giá chức năng tuyến yên điều khiển tinh hoàn sản xuất tinh trùng.*

### PCOS — 294× — suggested: `SPELL`
- *24 của em, có thể có nhiều nguyên nhân khác như: - Rối loạn nội tiết tố - Tình trạng như PCOS (hội chứng buồng trứng đa nang) - Căng thẳng, cân nặng thay đổi - Hoặc đơn giản là đặc*
- *ây tôi có đi khám phụ khoa và bác sĩ có chẩn đoán tôi bị **hội chứng buồng trứng đa nang (PCOS)**.*
- *Do chị có PCOS, kinh nguyệt có thể không đều và gây thiếu máu mạn tính.*

### CC — 284× — suggested: `SPELL`
- *Tình trạng hiện tại: - CC: Đau răng trong cùng, sưng nướu, đau nhói dữ dội khi cắn mạnh.*
- *Tình trạng hiện tại: - CC: Đau răng số 7, sưng nướu, đau nhói dữ dội khi cắn mạnh.*
- ***Thông tin đã có**: - **CC**: Đau đầu gối.*

### AHA — 255× — suggested: `SPELL`
- *Chăm Sóc Tăng Cường (Tối - Tuần 2-3 lần)** - **Tẩy tế bào chết nhẹ**: Dùng sản phẩm chứa AHA/BHA 1-2 lần/tuần để loại bỏ da cũ, giúp da sáng hơn.*
- ***Không dùng chung**: Tránh dùng Retinol chung với Vitamin C hay AHA/BHA trong cùng buổi tối lúc mới bắt đầu.*
- *- Da em còn trẻ, không cần dùng hoạt chất mạnh như Retinol hay AHA/BHA cao.*

### TIA — 244× — suggested: `SPELL`
- *- Tuy nhiên, tê tay thoáng qua có thể là TIA (cơn thiếu máu não thoáng qua) hoặc do nguyên nhân thần kinh cơ.*
- *Giải thích nguyên nhân có thể (TIA, chèn ép thần kinh, hạ huyết áp tư thế).*
- ***Cơn thiếu máu não thoáng qua (TIA)**: Dù không phải đột quỵ nhưng đây là cảnh báo nguy cơ đột quỵ trong tương lai, cần đánh giá sớm.*

### GATHERING — 237× — suggested: `STRIP`
- *Phase: GATHERING INFORMATION (Turn 5) - Moving to PHASE 3: PROVIDING STRUCTURE Patient Age: 62 Objective: Summarize findings,*
- *<phase_check> **Phase Check**: Tôi đang ở PHASE 2: GATHERING INFORMATION.*
- *<internal_reasoning** **Giai đoạn**: PHASE 2 - GATHERING INFORMATION (Turn 4).*

### RF — 228× — suggested: `SPELL`
- ***Các xét nghiệm cần thiết**: Bác sĩ có thể yêu cầu xét nghiệm máu (CRP, HLA-B27, RF), chụp X-quang hoặc MRI cột sống **Lưu ý an toàn**: Nếu em có triệu chứng nặng hơn như đau ngực*
- *sĩ nghi ngờ viêm khớp dạng thấp (do Anh/Chị có nhắc đến), họ sẽ chỉ định xét nghiệm máu (RF, anti-CCP) để loại trừ.*
- *động, sưng, đau ở các khớp - **Xét nghiệm máu**: Tìm yếu tố viêm (CRP, ESR), yếu tố thấp (RF), kháng thể anti-CCP (nếu nghi ngờ viêm khớp dạng thấp) - **Chụp X-quang**: Để xem tình*

### ENT — 227× — suggested: `SPELL`
- *- **Khuyến cáo**: Cần đi khám chuyên khoa Tai Mũi Họng (ENT) càng sớm càng tốt.*
- *hư đau họng lan tai, ngạt mũi, ù tai một bên, **Bác nên đi khám chuyên khoa Tai Mũi Họng (ENT) càng sớm càng tốt**.*
- ***: Dựa trên triệu chứng "thức ăn tràn vào mũi" là chính, anh nên đi khám **Tai Mũi Họng (ENT) trước**.*

### ANH — 220× — suggested: `LOWERCASE` → `anh`
- ***TÓM TẮT KẾ HOẠCH CỦA ANH**: - Áp dụng quy trình skincare 3 bước: Tẩy trang → Rửa mặt → Dưỡng ẩm + Kem chống nắng - Chọn kem chống nắng*
- *rên da khô - **Bước 2**: Rửa lại bằng sữa rửa mặt dịu nhẹ --- **TÓM LẠI QUY TRÌNH TỐI CHO ANH**: 1.*
- *--- **TÓM TẮT KẾ HOẠCH CỦA ANH TÙNG:** 1.*

### LH — 216× — suggested: `SPELL`
- *- **Xét nghiệm hormone sinh dục nam** (như Testosterone, FSH, LH) để kiểm tra xem có sự mất cân bằng nội tiết tố nào không.*
- *giá số lượng, chất lượng tinh trùng - **Xét nghiệm máu**: Kiểm tra hormone (testosterone, LH, FSH), đường huyết, chức năng thận gan - **Siêu âm**: Siêu âm tuyến tiền liệt, tinh hoà*
- *Xét nghiệm nội tiết tố máu**: - **FSH, LH**: Đánh giá chức năng tuyến yên điều khiển tinh hoàn sản xuất tinh trùng.*

### SAFETY — 213× — suggested: `STRIP`
- *ngay ✅ **Điều trị**: Tùy chẩn đoán, có thể dùng thuốc hoặc cần can thiệp chuyên sâu hơn **SAFETY NETTING (LƯU Ý AN TOÀN):** Anh Hùng à, nếu trong thời gian chờ đi khám, anh xuất hi*
- *Nếu có thể, nên có người đi cùng để hỗ trợ **SAFETY CHECK**: Tôi cần nhắc lại dấu hiệu nguy hiểm và đảm bảo em hiểu cần đi ngay.*
- ***AN TOÀN (SAFETY NETTING):** Nếu trong thời gian chờ đi khám, Lan thấy xuất hiện các dấu hiệu như: sưng đau da đầu, sốt, hoặc*

### PROVIDING — 211× — suggested: `STRIP`
- *Phase: GATHERING INFORMATION (Turn 5) - Moving to PHASE 3: PROVIDING STRUCTURE Patient Age: 62 Objective: Summarize findings, provide education using Ask-Tell-Ask method Safety C*
- ***PHASE 3: PROVIDING STRUCTURE** Trước tiên, Tôi muốn xác nhận: việc gia đình chuẩn bị chuyển bé lên Bệnh viện Ung bướu Hà Nội là*
- *<phase_check> **Phase Check**: Tôi đang ở PHASE 3: PROVIDING STRUCTURE.*

### EM — 203× — suggested: `LOWERCASE` → `em`
- ***EM CẦN NGHE KỸ NÀY**: Em **TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ MUA KHÁNG SINH UỐNG** nhé!*
- ***BƯỚC 2: NẾU EM KHÔNG THỂ GỌI (Vì sợ hoặc bất kỳ lý do gì)** - **Tìm kiếm "Trung tâm Tâm lý học đường"** hoặc **"Phòng khám T*
- *Nhưng điều quan trọng nhất em cần biết là: **EM KHÔNG PHẢI LÀ GÁNH NẶNG.*

### ADHD — 189× — suggested: `SPELL`
- *Rối loạn tăng động giảm chú ý (ADHD) - có thể xuất hiện sớm.*
- ***Đây là một dấu hiệu rất tốt!** Trẻ bị ADHD thường **khó tập trung vào các hoạt động cần suy nghĩ hoặc các công việc không phải là sở thích**, nhưng lại*
- *Nếu bé vẫn chơi xếp hình tốt, học hỏi nhanh, và giao tiếp tốt, thì khả năng bé bị ADHD là thấp.*

### PSA — 187× — suggested: `SPELL`
- *Xét nghiệm máu PSA để loại trừ các bệnh lý nghiêm trọng hơn nếu cần.*
- *Có thể thăm khám trực tiếp tuyến tiền liệt qua ngã trực tràng (nếu cần) - Xét nghiệm máu PSA (chỉ số ung thư) - thường chỉ làm khi có chỉ định **Chuẩn bị trước khi đi khám:** - **K*
- *n khoa Tiết niệu để được thăm khám trực tiếp - Các xét nghiệm có thể: nước tiểu, siêu âm, PSA nếu cần - Chuẩn bị: không cần kiêng cữ gì đặc biệt **Lưu ý an toàn:** Nếu em gặp bất k*

### ESR — 183× — suggested: `SPELL`
- *phù hợp - Các xét nghiệm cần làm: Công thức máu, chức năng đông máu, xét nghiệm viêm (CRP,ESR) - **Chuẩn bị**: Nhịn ăn 8-12 giờ trước khi lấy máu (chỉ uống nước lọc được) - Chi phí*
- ***Xét nghiệm máu:** * **Công thức máu và tốc độ máu lắng (ESR), CRP:** Để đánh giá xem trong cơ thể Bác có dấu hiệu viêm hay không.*
- *Xét nghiệm cần làm** (bác sĩ sẽ chỉ định): - **Xét nghiệm máu**: Đánh giá viêm (CRP, ESR), yếu tố dạng thấp, HLA-B27 (nếu nghi ngờ AS) - **Chẩn đoán hình ảnh**: - Chụp X-quang cột *

### THEO — 182× — suggested: `LOWERCASE` → `theo`
- *THEO DÕI TRIỆU CHỨNG**: - Trong 1-2 tuần, nếu triệu chứng giảm (ít chảy máu, bớt đau) thì tiếp tục.*
- *TRÁNH GÁNG SỨC NẶNG VÀ THEO DÕI TRIỆU CHỨNG** - **Lợi ích**: Ngăn ngừa cơn đau xuất hiện đột ngột.*
- *THEO DÕI TRIỆU CHỨNG Ghi lại trong sổ: - Khi nào cơn đau xuất hiện?*

### ALT — 181× — suggested: `SPELL`
- *khuyên em nên đi khám bác sĩ để được làm xét nghiệm máu kiểm tra chức năng gan (như AST, ALT, bilirubin) và siêu âm gan, giúp xác định chính xác nguyên nhân và có hướng điều trị ph*
- *ám bác sĩ chuyên khoa Gan mật để được làm xét nghiệm máu kiểm tra chức năng gan (như AST, ALT, bilirubin, albumin) và siêu âm gan.*
- ***Khi đi khám, bác sĩ có thể chỉ định**: - **Xét nghiệm máu**: Kiểm tra men gan (AST, ALT), bilirubin, chức năng gan - **Siêu âm gan**: Xem kích thước, cấu trúc gan có bình thường *

### AST — 180× — suggested: `SPELL`
- *h/chị khuyên em nên đi khám bác sĩ để được làm xét nghiệm máu kiểm tra chức năng gan (như AST, ALT, bilirubin) và siêu âm gan, giúp xác định chính xác nguyên nhân và có hướng điều *
- *đi khám bác sĩ chuyên khoa Gan mật để được làm xét nghiệm máu kiểm tra chức năng gan (như AST, ALT, bilirubin, albumin) và siêu âm gan.*
- ***Khi đi khám, bác sĩ có thể chỉ định**: - **Xét nghiệm máu**: Kiểm tra men gan (AST, ALT), bilirubin, chức năng gan - **Siêu âm gan**: Xem kích thước, cấu trúc gan có bình thường *

### SIDS — 177× — suggested: `SPELL`
- *, khi bé **ngủ**, chị **tuyệt đối phải cho bé nằm ngửa** để tránh nguy cơ đột tử sơ sinh (SIDS).*
- ***Về "hội chứng mông chết"**: Có thể chị đang nghe nói đến **SIDS (Sudden Infant Death Syndrome)** - hội chứng đột tử ở trẻ sơ sinh khi ngủ.*
- *Tuy nhiên, bé Hà đã 2 tuổi nên **không còn nguy cơ** về hội chứng này nữa, vì SIDS chỉ xảy ra ở trẻ dưới 1 tuổi, đặc biệt là 2-4 tháng tuổi.*

### VA — 175× — suggested: `SPELL`
- *iều), anh/chị nên đưa bé đi khám bác sĩ nhi để kiểm tra kỹ hơn và loại trừ viêm xoang hay VA.*
- *Trước giờ anh/chị có biết gì về tình trạng **viêm VA (viêm amidan mũi họng)** ở trẻ nhỏ không ạ?*
- *Em nghe thì hiểu là bé có thể bị viêm VA, nhưng em không chắc lắm.*

### RICE — 174× — suggested: `SPELL`
- *Về cách giảm đau nhanh để đi làm, anh/chị có thể áp dụng phương pháp **RICE**: 1.*
- *Vậy là chúng ta đã thống nhất Lan sẽ áp dụng phương pháp RICE, hạn chế vận động mạnh và chườm lạnh trong 2-3 ngày tới.*
- *Lan đã nghe qua phương pháp "RICE" (Nghỉ ngơi - Rest, Chườm lạnh - Ice, Băng ép - Compression, Nâng cao - Elevation) để giảm viêm chưa?*

### STI — 172× — suggested: `SPELL`
- *n cách đây 1 tuần, em cũng cần được kiểm tra để loại trừ các bệnh lây qua đường tình dục (STI) như lậu, chlamydia.*
- *Bác sĩ sẽ khám, lấy nước tiểu xét nghiệm, và có thể xét nghiệm STI nếu cần.*
- *tiện đi khám phụ khoa, các phòng khám đa khoa cũng có thể xét nghiệm nước tiểu và tư vấn STI được.*

### IUI — 169× — suggested: `SPELL`
- ***Sự khác biệt giữa IUI và IVF:** **IUI (Intrauterine Insemination):** - Bác sĩ sẽ bơm tinh trùng đã được rửa sạch trực tiếp vào tử c*
- ***Sự khác biệt giữa IUI và IVF:** **IUI (Intrauterine Insemination):** - Bác sĩ sẽ bơm tinh trùng đã được rửa sạch trực tiếp vào tử cung vào thời điể*
- *Em đã tìm hiểu gì về các phương pháp điều trị hỗ trợ sinh sản (IUI, IVF) mà bác sĩ đề cập chưa?*

### QRS — 163× — suggested: `SPELL`
- *QRS rộng*
- *Thực ra, điều em mong muốn nhất hôm nay là muốn hiểu rõ hơn về tình trạng "QRS rộng" này.*
- *đập nhanh và mệt mỏi thì chắc hẳn em đang rất lo lắng, đặc biệt là khi bác sĩ có nhắc đến QRS bị rộng.*

### STRUCTURE — 160× — suggested: `STRIP`
- *Phase: GATHERING INFORMATION (Turn 5) - Moving to PHASE 3: PROVIDING STRUCTURE Patient Age: 62 Objective: Summarize findings, provide education using Ask-Tell-Ask method Safety Che*
- ***PHASE 3: PROVIDING STRUCTURE** Trước tiên, Tôi muốn xác nhận: việc gia đình chuẩn bị chuyển bé lên Bệnh viện Ung bướu Hà Nội là **hoàn toà*
- *<phase_check> **Phase Check**: Tôi đang ở PHASE 3: PROVIDING STRUCTURE.*

### ACE — 160× — suggested: `SPELL`
- *- **Cao huyết áp**: Cần lưu ý thuốc đang dùng (thường là lợi tiểu, ức chế ACE/ARB) có thể gây tác dụng phụ, nhưng không giải thích rõ ràng toàn bộ picture (sốt, sút cân, đau họng).*
- *đủ**: Tiền sử HTN, thuốc Amlodipin (thuốc chẹn kênh canxi, có thể gây ho nhưng ít gặp hơn ACE inhibitors).*
- *Đây là thông tin quan trọng để hiểu nguyên nhân tiềm ẩn (ví dụ: ho do thuốc ACE inhibitors, ho do trào ngược, hen suyễn...).*

### COMPLETE — 158× — suggested: `STRIP`
- ***Thêm [COMPLETE]**: Vì bệnh nhân xác nhận đã hài lòng và không còn thắc mắc.*
- *Cần chúc sức khỏe và thêm tag [COMPLETE] để đánh dấu phiên tư vấn thành công.*
- *- Đóng tag [COMPLETE].*

### INFORMATION — 157× — suggested: `STRIP`
- *Phase: GATHERING INFORMATION (Turn 5) - Moving to PHASE 3: PROVIDING STRUCTURE Patient Age: 62 Objective: Summarize findings, provide educ*
- *<phase_check> **Phase Check**: Tôi đang ở PHASE 2: GATHERING INFORMATION.*
- *<internal_reasoning** **Giai đoạn**: PHASE 2 - GATHERING INFORMATION (Turn 4).*

### COVID — 154× — suggested: `SPELL`
- *Nhưng con vẫn lo là không biết có phải con bị COVID không nữa?*
- *Con có cần đi test COVID không?*
- *- Bệnh nhân đã hiểu và có kế hoạch hành động cụ thể (test COVID, nghỉ ngơi, theo dõi, đi khám nếu không đỡ).*

### PPI — 153× — suggested: `SPELL`
- *- **Thuốc men**: Nếu nặng, bác sĩ có thể kê thuốc giảm acid (thường là PPI), nhưng sẽ điều trị theo đợt, không phải uống vĩnh viễn.*
- *Thuốc thường được bác sĩ chỉ định trong trường hợp này là nhóm **thuốc ức chế bơm proton (PPI)** (ví dụ: Omeprazole, Pantoprazole...).*
- *i ý bệnh nhân nên quay lại bác sĩ để được kê đơn thuốc kháng acid hoặc ức chế bơm proton (PPI) nếu cần, vì triệu chứng ảnh hưởng đến chất lượng cuộc sống.*

### KHOA — 152× — suggested: `SPELL`
- *DÙNG CHỈ NHA KHOA**: - **Thời gian**: 1 lần/ngày (tối trước khi đánh răng).*
- *ÔNG thể chẩn đoán chính xác** thay bác sĩ, nhưng con **KHUYẾN NGHỊ BÁC NÊN ĐI KHÁM CHUYÊN KHOA TIM MẠCH NGAY** để được làm các xét nghiệm cần thiết như điện tâm đồ, siêu âm tim, ho*
- ***ĐƯA BÉ ĐI KHÁM BÁC SĨ NHI KHOA** trong thời gian sớm nhất để được chẩn đoán chính xác và điều trị phù hợp 3.*

### OCT — 151× — suggested: `SPELL`
- *Nếu được, chọn bệnh viện có thể chụp cắt lớp võng mạc (OCT) hoặc siêu âm mắt để xác định chính xác tình trạng.*
- *a mắt càng sớm càng tốt để bác sĩ kiểm tra đáy mắt, có thể cần chụp mạch huỳnh quang hoặc OCT để xác định chính xác tình trạng và có phương pháp điều trị phù hợp.*
- ***Chụp cắt lớp võng mạc (OCT)**: Đây là chụp ảnh không xâm lấn, giúp nhìn rõ cấu trúc võng mạc chi tiết.*

### CLOSING — 148× — suggested: `SPELL`
- *<think> **Kiểm tra giai đoạn**: Tôi đang ở PHASE 4 (CLOSING).*
- ***PHASE 4: CLOSING** Tôi rất hiểu lo lắng của anh/chị.*
- *<think> **Kiểm tra giai đoạn:** PHASE 4 - CLOSING **Thông tin:** - Bác đã hiểu và quyết định đi khám tim mạch - Câu hỏi cuối: Có cần mang sổ theo dõi huyết áp*

### CPAP — 147× — suggested: `SPELL`
- *ngủ (sleep study) để chẩn đoán chính xác - Được tư vấn điều trị phù hợp (có thể dùng máy CPAP) **Trong lúc chờ đi khám:** - Tránh lái xe hay vận hành máy móc nguy hiểm - Giữ giờ gi*
- *dù em nói không có gì nghiêm trọng) **Về điều trị:** - **Không phức tạp**: Chủ yếu là máy CPAP (máy trợ thở qua mặt nạ khi ngủ) - **Hiệu quả nhanh**: Sau 1-2 tuần là em sẽ thấy khá*
- *ó thể theo dõi nếu em có triệu chứng bất thường trong lúc ngủ, hoặc giúp nhắc em dùng máy CPAP - Nếu em ngại, có thể chỉ cần báo 1-2 người thân thiết nhất **Tóm lại**: Điều trị sẽ *

### DIY — 146× — suggested: `SPELL`
- *Tôi cũng hay làm DIY decor cho nhà cửa, có thể do tôi thường xuyên dùng tua vít hay các dụng cụ nhỏ không ạ?*
- *- Anh/Chị thường xuyên làm vườn (vun đất, bón phân) và DIY (dùng tua vít), những động tác này lặp lại nhiều lần ở ngón tay và cổ tay, có thể gây viêm gân.*
- *Tôi hiểu rồi, có thể do tôi làm vườn và DIY nhiều nên bị viêm gân, hoặc cũng có thể do cú té trước đó.*

### HDL — 145× — suggested: `SPELL`
- ***Lipidogram**: Kiểm tra lại cholesterol (tổng cholesterol, LDL, HDL) để đánh giá chính xác tình trạng của em.*
- *(LDL, HDL, Total) - Cô ấy có gặp tác dụng phụ gì với Atorvastatin không?*
- *ạch hoặc nội tiết để được đánh giá chi tiết - Yêu cầu xét nghiệm cholesterol đầy đủ (LDL, HDL, triglycerides, cholesterol toàn phần) - Thảo luận về các lựa chọn điều trị phù hợp vớ*

### ABCDE — 143× — suggested: `SPELL`
- *Chúng ta có thể nhớ theo quy tắc **ABCDE**: - **A (Asymmetry - Không đối xứng)**: Nốt ruồi bị méo mó, một bên không đều với bên kia.*
- *Với nốt ruồi của em, em thấy có điểm nào trong ABCDE không?*
- *Em đã ghi nhớ quy tắc ABCDE này để tự theo dõi.*

### DM — 140× — suggested: `SPELL`
- *- Tiền sử: HTN, DM, BPH.*
- *Hỏi về tiền sử bệnh lý (PMH) để tìm yếu tố nguy cơ (gout, HTN, DM).*
- *- Nếu ống dẫn bị hẹp (do mảng bám, hút thuốc, HTN, DM), oxy không đến đủ -> đau ngực.*

### GED — 140× — suggested: `SPELL`
- *Tôi đang cố gắng học để thi lấy bằng GED và học thêm về quản lý nhà hàng để thăng tiến.*
- *- Tôi cần giải thích về quá trình hồi phục - Tôi cần trả lời trực tiếp câu hỏi của em về GED và làm game - Tôi cần kết hợp với thông tin về việc điều trị hiện đại giúp giảm tác dụn*
- *lời em một cách chân thành và hy vọng: **CÂU TRẢ LỜI LÀ: CÓ, HOÀN TOÀN CÓ THỂ!** **Về học GED**: Nhiều người sau điều trị ung thư vẫn tiếp tục học tập và thi đỗ.*

### OSA — 136× — suggested: `SPELL`
- *hẹ** - tôi rất lo lắng cho anh về một tình trạng gọi là **ngưng thở khi ngủ do tắc nghẽn (OSA)**.*
- ***Về ngưng thở khi ngủ**: Nếu anh bị chẩn đoán OSA, có một số cách **hỗ trợ** tại nhà, nhưng **KHÔNG thay thế** việc điều trị y khoa: 1.*
- *tiếng mỗi đêm **Tóm lại**: Anh cần đi khám chuyên khoa hô hấp để xác định chính xác có bị OSA không, và quay lại bác sĩ sinh sản để hiểu rõ hơn về AMH.*

### OTC — 135× — suggested: `SPELL`
- *Nếu cơn đau quá khó chịu trước khi đi khám, bác có thể dùng thuốc giảm đau không kê đơn (OTC) để tạm thời giảm bớt, nhưng nên hỏi ý kiến dược sĩ về loại thuốc phù hợp và liều dùng *
- *Em chỉ còn một thắc mắc nho nhỏ: Em có thể mua thuốc giảm đau không cần toa bác sĩ (thuốc OTC) để dùng không?*
- *Nếu cần thiết, sẽ đi hỏi dược sĩ về thuốc giảm đau OTC thay vì tự ý mua dùng.*

### H5 — 133× — suggested: `SPELL`
- *Cúm A H5*
- *Tôi đang nghi ngờ mình bị cúm A H5.*
- *Tôi có nghe nói về cúm A H5 gì đó gần đây, không biết có phải không.*

### FNA — 128× — suggested: `SPELL`
- *nh: - **Siêu âm vú**: để xem rõ đặc điểm khối u và dịch - **Chọc hút tế bào bằng kim nhỏ (FNA)** hoặc **sinh thiết**: để lấy mẫu xét nghiệm nếu cần - **Chụp nhũ ảnh (mammogram)**: *
- *Nếu cần thiết hoặc nghi ngờ, bác sĩ có thể chỉ định **chọc hút tế bào (FNA)** hoặc **sinh thiết** để xét nghiệm tế bào, nhưng thường chỉ làm khi có nghi ngờ gì đó bất thường.*
- ***Chọc hút tế bào (FNA)**: Chỉ làm nếu bác sĩ nghi ngờ hoặc cần chẩn đoán chắc chắn trước khi quyết định điều trị Quy trình này thườ*

### UVA — 127× — suggested: `SPELL`
- *ng nắng (bắt buộc)** - Anh nên dùng kem chống nắng có SPF 30-50, broad spectrum (chống cả UVA và UVB).*
- ***Công nghệ mới**: Nên chọn loại có ghi "Broad Spectrum" hoặc PA+++ để bảo vệ khỏi cả tia UVA (gây lão hóa) và UVB (gây cháy nắng).*
- *Vì: - Tia UVA xuyên qua cửa kính và màn hình máy tính.*

### DVT — 121× — suggested: `SPELL`
- *- **Red Flags**: Đã loại trừ DVT cấp (không đau, không đỏ, không nóng), không nhiễm trùng.*
- *=> Loại trừ DVT cấp tính và nhiễm trùng.*
- *- Cần loại trừ huyết khối tĩnh mạch sâu (DVT), thuyên tắc phổi (PE), nhiễm trùng tế bào, loét.*

### TMJ — 119× — suggested: `SPELL`
- *khi thức dậy là những dấu hiệu rất điển hình của tình trạng rối loạn khớp thái dương-hàm (TMJ) hoặc do nghiến răng khi ngủ.*
- *rạng **nghiến răng khi ngủ (bruxism)** và có thể kèm theo **rối loạn khớp thái dương-hàm (TMJ)**.*
- *hi ngủ, và đau đầu hai bên thái dương - đây rất có thể là **rối loạn khớp thái dương hàm (TMJ)**, thường do nghiến răng và căng thẳng gây ra.*

### SINH — 118× — suggested: `SPELL`
- ***EM CẦN NGHE KỸ NÀY**: Em **TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ MUA KHÁNG SINH UỐNG** nhé!*
- ***VỆ SINH GIẤC NGỦ - HƯỚNG DẪN CHI TIẾT:** **Thời gian:** - Đi ngủ: 10-10:30 tối (muộn nhất 11 giờ) - Dậy: 6-6:30 sáng*
- *ĐIỀU CẦN TRÁNH TRONG SINH HOẠT** - **Mang vác nặng**: Tránh xách túi xách nặng, mang vác vật cồng kềnh.*

### EEG — 118× — suggested: `SPELL`
- *Họ có thể đề nghị làm một số xét nghiệm như: - **Đo điện não đồ (EEG)**: Để xem hoạt động điện trong não khi ngủ.*
- ***Chụp EEG (điện não đồ)**: Kiểm tra hoạt động điện não khi ngủ 2.*
- ***Xét nghiệm chuyên sâu về thần kinh**: - **Điện não đồ (EEG)**: Nếu cần đánh giá hoạt động điện của não - **Các test chức năng tiền đình**: Để đánh giá nguyên nhân chóng*

### UVB — 117× — suggested: `SPELL`
- *(bắt buộc)** - Anh nên dùng kem chống nắng có SPF 30-50, broad spectrum (chống cả UVA và UVB).*
- *n chọn loại có ghi "Broad Spectrum" hoặc PA+++ để bảo vệ khỏi cả tia UVA (gây lão hóa) và UVB (gây cháy nắng).*
- *cảm:** Bác nên chọn kem chống nắng có ghi dòng chữ **"Broad Spectrum"** (bảo vệ cả UVA và UVB) với chỉ số SPF từ 30 đến 50.*

### SCID — 113× — suggested: `SPELL`
- *Bệnh SCID*
- *bệnh viện ngay - **Không tự ý ngưng thuốc kháng sinh** dù đã đỡ **Lưu ý quan trọng**: Với SCID, nhiễm trùng có thể diễn tiến rất nhanh.*
- *SCID là một tình trạng suy giảm miễn dịch rất nghiêm trọng, việc bác quan tâm đến cách chăm sóc bản thân là điều r*

### TRONG — 112× — suggested: `SPELL`
- *u ngón tay massage nhẹ nhàng theo vòng tròn trong 2-3 phút **DINH DƯỠNG TỐT CHO DA TỪ BÊN TRONG:** - **Uống đủ nước**: 1.5-2 lít nước/ngày - **Ăn nhiều**: Rau xanh, trái cây (đặc b*
- *Ghi chú huyết áp hàng ngày của bác (nếu có máy đo) **TRONG THỜI GIAN CHỜ ĐI KHÁM, LƯU Ý:** - **Tránh các hoạt động nặng**: khuân vác, lau dọn nhiều, tập thể dục gắng sứ*
- *trên 38.5°C kèm đau khớp - Khó thở, đau ngực - Mất khả năng đi lại đột ngột **CẦN ĐI KHÁM TRONG 1-2 NGÀY TỚI:** - Đau không giảm sau 2 tuần nghỉ tập và điều chỉnh - Đau tăng lên, l*

### NIPT — 110× — suggested: `SPELL`
- *đình và có ý định mang thai, em sẽ được tư vấn về **chẩn đoán trước sinh** như xét nghiệm NIPT (xét nghiệm máu mẹ từ tuần 10-12 thai kỳ) hoặc chọc ối/sinh thiết gai nhau để kiểm tr*
- *con em là thông qua **chẩn đoán trước sinh** khi em mang thai, bao gồm các xét nghiệm như NIPT (xét nghiệm máu mẹ), chọc ối hoặc sinh thiết gai nhau để kiểm tra NST của thai nhi.*
- *Em đang mang thai 13 tuần và nhận kết quả NIPT dương tính với nguy cơ Hội chứng Edwards, tôi hoàn toàn hiểu cảm giác sợ hãi và lo lắng của em lúc này.*

### ANA — 109× — suggested: `SPELL`
- *Để biết chính xác, em cần làm xét nghiệm máu (kiểm tra yếu tố Rheumatoid, CRP, ANA...) và chụp hình ảnh khớp.*
- *SR), CRP (chỉ số viêm) - Yếu tố dạng thấp (RF) và kháng thể anti-CCP - Kháng thể tự miễn: ANA, anti-SSA/SSB (nếu nghi ngờ hội chứng Sjögren) - Chức năng gan, thận - X-quang khớp để*
- ***Xét nghiệm nếu cần**: - Xét nghiệm máu: CRP, tốc độ máu lắng, yếu tố dạng thấp, ANA...*

### SAU — 108× — suggested: `LOWERCASE` → `sau`
- ***SAU ĐÓ PHẢI KÊU GỌI BÁC ĐI KHÁM NGAY** **Câu hỏi cuối cùng trước khi đưa ra khuyến nghị:** "Bác đang uống thuốc c*
- **Tránh vừa ăn vừa nói**: Dễ bị sặc **Lưu ý quan trọng:** Bác chỉ nên áp dụng các cách này SAU KHI đã đi khám và bác sĩ xác nhận không có vấn đề nghiêm trọng.*
- *Em cần nói chuyện với người lớn ngay bây giờ.** **HÃY LÀM NGAY NHỮNG VIỆC SAU:** 1.*

### HIV — 106× — suggested: `SPELL`
- *Em có bị HIV hay các bệnh suy giảm miễn dịch không?*
- *Em cũng không bị HIV hay các bệnh suy giảm miễn dịch gì cả.*
- *độ, tình trạng mệt mỏi, đổ mồ hôi đêm - **Tiền sử bệnh**: Ghi rõ em không có tiền sử lao, HIV, không tiếp xúc với người bệnh lao **2.*

### B1 — 106× — suggested: `SPELL`
- ***Thiếu chất**: Em nghĩ đúng đấy, thiếu một số vitamin như B12, B1 có thể gây tê bì chân tay.*
- *hư: - Thuốc giảm đau thần kinh (ví dụ: gabapentin, pregabalin) - Vitamin nhóm B (đặc biệt B1, B6, B12) bổ sung thần kinh - Các thuốc điều hòa thần kinh khác 3.*
- *À, mà cháu có hay uống vitamin B1 và B12 để bổ sung cho chắc người ạ.*

### RLS — 105× — suggested: `SPELL`
- *- **Bước 2**: Bác sĩ có thể điều chỉnh thuốc huyết áp hoặc kê đơn thuốc đặc trị cho RLS nếu cần.*
- *điển hình của tình trạng bứt rứt chân tay, hay còn gọi là hội chứng chân không yên nghỉ (RLS).*
- *hể bác đang gặp phải tình trạng **hội chứng chân không yên nghỉ (Restless Legs Syndrome - RLS)**.*

### TIN — 104× — suggested: `SPELL`
- *THÔNG TIN CÁ NHÂN**: - Tiền sử bệnh: __ (tiểu đường, tim mạch, ung thư...) - Thuốc đang dùng: __ - Tiếp xúc nguồn lây:*
- *ói ạ." - Sau đó chỉ cần kể: "Con đau bụng, đi ngoài ra máu, có khối u ở bụng." **ĐỂ BỐ MẸ TIN CHÁU HƠN:** - Nhấn mạnh: "Con đã bị như vậy **mấy tuần nay rồi**" (nếu đúng) - Nói: "C*
- *không?) - Đơn thuốc (nếu có) - Thẻ bảo hiểm y tế, CCCD - Giấy tờ tùy thân khác **📝 THÔNG TIN NÊN GHI CHÉP TRƯỚC**: 1.*

### GIAN — 101× — suggested: `SPELL`
- *MỐC THỜI GIAN ĐI KHÁM:** Anh nên tập luyện và theo dõi trong **2-4 tuần**.*
- *Ghi chú huyết áp hàng ngày của bác (nếu có máy đo) **TRONG THỜI GIAN CHỜ ĐI KHÁM, LƯU Ý:** - **Tránh các hoạt động nặng**: khuân vác, lau dọn nhiều, tập thể dục gắng sức - **Giữ*
- *GIẢI PHÁP TRONG THỜI GIAN NGHĨ TẬP (1-2 TUẦN):** **Duy trì thể lực:** - **Đi bộ nhẹ nhàng**: Giảm xuống 2-3km, đi chậm, chọn đường bằng*

### PT — 100× — suggested: `SPELL`
- ***Xét nghiệm đông máu**: Kiểm tra chức năng đông máu (thường là PT, aPTT).*
- ***Vật lý trị liệu (PT):** Đây là phương pháp rất quan trọng.*
- ***Tập vật lý trị liệu (PT)**: Đây là cách tốt nhất.*

### ABI — 100× — suggested: `SPELL`
- *yên khoa **Lồng ngực - Mạch máu** để bác sĩ đo chỉ số lưu lượng máu ở chân (gọi là chỉ số ABI).*
- *Đi khám chuyên khoa **Lồng ngực - Mạch máu** để được đo chỉ số ABI và siêu âm mạch máu chân trái.*
- *h hoặc Lồng ngực - Mạch máu để được: - Thăm khám trực tiếp - Đo chỉ số huyết áp bàn chân (ABI) - Siêu âm mạch máu nếu cần **Lưu ý an toàn:** Nếu bác thấy cơn đau không hết khi nghỉ*

### B6 — 97× — suggested: `SPELL`
- *- Thuốc giảm đau thần kinh (ví dụ: gabapentin, pregabalin) - Vitamin nhóm B (đặc biệt B1, B6, B12) bổ sung thần kinh - Các thuốc điều hòa thần kinh khác 3.*
- *Vitamin nhóm B (đặc biệt B1, B6, B12) giống như lớp vỏ bọc cách điện cho các dây này vậy.*
- *Vitamin B1, B6, và B12 đóng vai trò quan trọng trong việc bảo vệ và phục hồi dây thần kinh.*

### WPW — 96× — suggested: `SPELL`
- ***Tình huống**: Bệnh nhân WPW có triệu chứng rõ ràng: - Cơn tim đập nhanh 15-20 phút, xuất hiện khi làm việc nặng/căng thẳng, đỡ khi nghỉ -*
- *mệt mỏi khi làm việc nặng **Phân tích lâm sàng**: - Đây là các triệu chứng điển hình của WPW có thể gây cơn nhịp nhanh qua đường phụ (tachycardia).*
- *- Cần khai thác thêm: tiền sử bệnh lý, thuốc men đang dùng, đặc biệt là thuốc điều trị WPW.*

### CLL — 92× — suggested: `SPELL`
- *u chứng mệt mỏi, sốt nhẹ, đau nhức xương và bứt rứt gần hai tuần, trong khi đang điều trị CLL bằng ibrutinib.*
- ***Tóm tắt lại những điểm chính**: - Bác đang điều trị CLL bằng ibrutinib - Triệu chứng: mệt mỏi, sốt nhẹ (~37.5°C) chiều tối, đau nhức xương, bứt rứt gần 2 tuần - Bác*
- *Con hiểu bác đã được chẩn đoán CLL từ tháng 10/2023 và đang rất lo lắng về diễn tiến của bệnh.*

### ER — 91× — suggested: `SPELL`
- *g:** I must mention that if he feels very weak, dizzy, or nauseous, he needs to go to the ER immediately (Addisonian crisis).*
- ***Safety netting**: Nhắc lại các dấu hiệu nguy hiểm cần đi ER ngay.*
- *ng, tranh cãi - Tránh rượu bia (dù chỉ là rượu vang) - Tránh thức khuya **DẤU HIỆU CẦN ĐI ER NGAY LẬP TỨC:** - Đau đầu tăng đột ngột, dữ dội hơn - Mắt mờ đột ngột, mất thị lực - Yế*

### H1N1 — 91× — suggested: `SPELL`
- **nhiễm trùng hô hấp trên** (viêm họng cấp), không phải bệnh liên cầu khuẩn ở lợn (cúm heo/H1N1) đâu ạ.*
- ***Trước hết, Tôi xin chia sẻ ngắn gọn:** Cúm heo (H1N1) là bệnh lây từ heo sang người, gây sốt cao, ho khan, đau đầu, mệt mỏi và có thể khó thở.*
- *với lợn, khiến tôi nghĩ đến khả năng anh bị nhiễm trùng đường hô hấp, có thể là cúm heo (H1N1) như anh lo ngại.*

### NOT — 90× — suggested: `SPELL`
- *cope - I can explain the typical process of seeing a doctor for this condition - I should NOT prescribe specific medications or dosages - I should prepare her for what information *
- *Address her expectation about "definitive treatment" - Ask if she has questions I should NOT: - Diagnose - Prescribe - Provide specific medical advice beyond "see a doctor" Let me *
- *Therefore, it is **NOT Albinism**.*

### GIAI — 87× — suggested: `SPELL`
- ***KIỂM TRA GIAI ĐOẠN**: Giai đoạn 4 (Closing).*
- ***KIỂM TRA GIAI ĐOẠN**: Giai đoạn 3 (Providing Structure).*
- *<think> **GIAI ĐOẠN**: Tôi đang ở **PHASE 2: GATHERING INFORMATION**.*

### HRT — 85× — suggested: `SPELL`
- ***Liệu pháp hormone (HRT)**: Giúp điều hòa kinh nguyệt, giảm triệu chứng, và bảo vệ sức khỏe xương.*
- ***Giải thích các lựa chọn**: Nhắc đến liệu pháp hormone thay thế (HRT) và các lựa chọn khác 3.*
- ***Liệu pháp hormone thay thế (HRT)**: Có thể giúp giảm bốc hỏa, thay đổi cân nặng, và các triệu chứng khác của mãn kinh.*

### QT — 85× — suggested: `SPELL`
- *Hội chứng QT kéo dài*
- ***Về hội chứng QT kéo dài:** Đây là tình trạng tim có thể gây loạn nhịp nguy hiểm, nhưng chỉ bác sĩ tim mạch qua điện tâm đồ (E*
- *Em rất lo lắng về QT kéo dài, vì em có tìm hiểu thì thấy nó có thể gây đột tử.*

### HA — 84× — suggested: `SPELL`
- **thành phần** kem dưỡng ẩm an toàn, dễ tìm: **Thành phần nên có:** - **Hyaluronic acid** (HA): Giữ nước tốt, không gây kích ứng - **Ceramide**: Phục hồi hàng rào da, rất phù hợp da*
- ***Dưỡng ẩm**: Kem dưỡng ẩm có chứa Hyaluronic Acid (HA) hoặc Ceramide, giúp da căng mọng và giảm nhìn thấy nếp nhăn.*
- ***Thành phần dưỡng ẩm**: Nên tìm các sản phẩm chứa **Hyaluronic Acid** (HA) hoặc **Glycerin** để cấp nước cho da, giúp da căng mịn hơn.*

### THAY — 83× — suggested: `SPELL`
- *THAY ĐỔI LỐI SỐNG** - **Ngủ đủ giấc**: 7-8 tiếng, hạn chế thức khuya - **Uống đủ nước**: 2-2.5 lít nước/ngày - **H*
- *THAY ĐỔI CÁCH CHĂM SÓC TÓC:** - **Ngưng ngay** dầu gội có chất tẩy rửa mạnh (sulfate).*
- *THAY ĐỔI LỐI SỐNG GIÚP GIẢM ĐAU:** **a.*

### ATM — 83× — suggested: `SPELL`
- *phức tạp đâu: **Em cần mang theo:** - **CMND/CCCD** để đăng ký khám - **Tiền** hoặc **thẻ ATM** để đóng phí khám **Em không cần mang theo:** - Hồ sơ bệnh án (vì em nói không có bện*
- *Anh/chị có thể: - Hỏi trực tiếp bệnh viện trước khi đi - Mang theo tiền mặt và thẻ ATM để linh hoạt **Về thuốc sắt nếu được kê đơn:** - **Tác dụng phụ thường gặp**: Có thể gây táo *
- *iệm máu - Tăng cường thực phẩm giàu sắt ngay từ bây giờ - **Nhớ mang theo tiền mặt và thẻ ATM** khi đi khám **Lưu ý an toàn cuối cùng:** Nếu anh/chị thấy chóng mặt nặng hơn, ngất x*

### H5N1 — 82× — suggested: `SPELL`
- *Cúm A H5N1*
- *Về cúm A H5N1, bác yên tâm là loại này chủ yếu lây từ gia cầm sang người, và thường có triệu chứng rất nặng ngay từ đầu (số*
- *Tôi nghe nói gần đây có dịch cúm A H5N1, không biết triệu chứng của tôi có giống không?*

### IPL — 81× — suggested: `SPELL`
- *yên sâu**: Đến bác sĩ da liễu để được tư vấn các phương pháp như laser, peel da, ánh sáng IPL - hiệu quả nhanh hơn nhưng cần làm tại cơ sở y tế uy tín **Về mất ngủ gần đây:** Đây c*
- *Bác sĩ có thể đề xuất laser (như Q-switched), peel da hóa học hoặc lột da bằng ánh sáng (IPL) để loại bỏ hoàn toàn.*
- ***Các liệu pháp ánh sáng**: Laser, IPL (ánh sáng xung cường độ cao) - hiệu quả nhanh, nhưng chi phí cao hơn và cần bảo vệ da kỹ sau điều trị.*

### PRP — 80× — suggested: `SPELL`
- ***Tiêm khớp**: Tiêm huyết tương giàu tiểu cầu (PRP) hoặc acid hyaluronic nếu đau nhiều, có thể giúp giảm đau vài tháng.*
- *Nhiều người hồi phục bằng: - Vật lý trị liệu - Tiêm huyết tương giàu tiểu cầu (PRP) - Nghỉ ngơi và tập phục hồi chức năng **Thời gian hồi phục**: Nếu mổ, thường 3-6 tháng mới có th*
- *Bác hỏi về tiêm huyết tương giàu tiểu cầu (PRP) và tế bào gốc - đây là các phương pháp mới bác nghe nói đến đúng không ạ?*

### CNC — 80× — suggested: `SPELL`
- *Em làm công nhân trong xưởng sản xuất, hay phải dùng máy CNC và thao tác lặp đi lặp lại một.*
- *Em là thợ hàn CNC, đang làm việc thì em cảm thấy đau ở ngực phải, sau đó em sờ vào thì thấy nó to ra và đau.*
- *Bác làm kỹ sư cơ khí, trước đây bác rất minh mẫn, làm việc với CAD, CNC cả ngày mà không sao.*

### TRA — 78× — suggested: `SPELL`
- ***KIỂM TRA GIAI ĐOẠN**: Giai đoạn 4 (Closing).*
- ***KIỂM TRA GIAI ĐOẠN**: Giai đoạn 3 (Providing Structure).*
- *<think> **KIỂM TRA GIAI ĐOẠN**: Tôi đang ở **PHASE 4: CLOSING**.*

### CHI — 75× — suggested: `SPELL`
- ***VỆ SINH GIẤC NGỦ - HƯỚNG DẪN CHI TIẾT:** **Thời gian:** - Đi ngủ: 10-10:30 tối (muộn nhất 11 giờ) - Dậy: 6-6:30 sáng (đủ 7-8 tiếng) - Nghỉ trư*
- *thoại trên giường - Không ăn no trước khi ngủ 2-3 giờ **TẬP THỂ DỤC NHẸ NHÀNG - HƯỚNG DẪN CHI TIẾT:** **Buổi sáng (sau khi dậy):** - 10-15 phút: Vươn vai, xoay cổ, gập duỗi lưng - *
- *mạng - Nếu cần **phẫu thuật electives (lựa chọn)**, bác có thể về nhà chuẩn bị thêm **VỀ CHI PHÍ:** - Nếu có **bảo hiểm y tế**, phần lớn chi phí sẽ được chi trả - Nếu không có bảo *

### NAY — 74× — suggested: `SPELL`
- *--- **TÓM TẮT PHIÊN TƯ VẤN HÔM NAY:** ✅ **Triệu chứng chính**: Mệt mỏi, đau bụng dưới sườn phải (4-5/10), chán ăn, buồn nôn, vàng da/vàng mắt.*
- ***Sổ hộ khẩu** (để làm thủ tục bảo hiểm) **Việc em cần làm NGAY HÔM NAY:** 1.*
- ***Bác CẦN ĐI KHÁM NGAY HÔM NAY hoặc NGÀY MAI** tại bệnh viện có chuyên khoa Tim mạch.*

### ICSI — 73× — suggested: `SPELL`
- *- **IVF (Thụ tinh trong ống nghiệm)**: Phù hợp khi tinh trùng yếu nhiều hoặc AMH thấp - **ICSI (Tiêm tinh trùng vào trứng)**: Dùng cho tinh trùng rất yếu Quyết định cuối cùng sẽ ph*
- *- **ICSI (Tiêm tinh trùng vào trứng)**: Dùng cho tinh trùng rất yếu, chỉ cần 1 tinh trùng khỏe để tiêm vào trứng.*
- *Nếu tinh hoàn còn một phần chức năng, vẫn có thể có con tự nhiên hoặc hỗ trợ (IVF, ICSI).*

### INT — 73× — suggested: `SPELL`
- *the the I I I I the the I I I I the the I I, I the I I I I I I- ** I I I I the I I I INT INT I I I I I I I I I I INT INT INT I I INT INT INT INT I I I INT INT INT INT INT INT INT I*
- *the the I I I I the the I I I I the the I I, I the I I I I I I- ** I I I I the I I I INT INT I I I I I I I I I I INT INT INT I I INT INT INT INT I I I INT INT INT INT INT INT INT I*
- *I I I I the the I I, I the I I I I I I- ** I I I I the I I I INT INT I I I I I I I I I I INT INT INT I I INT INT INT INT I I I INT INT INT INT INT INT INT INT INT INT INT INT INT I*

### NONE — 72× — suggested: `SPELL`
- *Tôi nghe anhNONENONENONENONE" " " " " " " " " " " " " " NONE NONE NONENONENONE�" � NONE*
- *ng uống x x uống uống " uống x x x:: "" uống uống:: " "" " " " : " ::::: ": ":" ": ":: "" NONE NONENONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE N*
- *ng uống " uống x x x:: "" uống uống:: " "" " " " : " ::::: ": ":" ": ":: "" NONE NONENONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE NONE *

### QUESTION — 70× — suggested: `SPELL`
- *o know when to expect improvement - **E**xpectations: Looking for timeline for recovery **QUESTION COUNT**: Patient is asking a question, not me.*
- ***QUESTION COUNT**: Đây là câu hỏi cuối cùng của em, tôi không cần hỏi thêm.*
- *i cần nhắc lại red flags một lần nữa để đảm bảo an toàn - Kết thúc ấm áp, chuyên nghiệp **QUESTION COUNT**: KHÔNG hỏi thêm câu nào.*

### TIM — 69× — suggested: `LOWERCASE` → `tim`
- *hể chẩn đoán chính xác** thay bác sĩ, nhưng con **KHUYẾN NGHỊ BÁC NÊN ĐI KHÁM CHUYÊN KHOA TIM MẠCH NGAY** để được làm các xét nghiệm cần thiết như điện tâm đồ, siêu âm tim, hoặc te*
- *KHÁM CHUYÊN KHOA TIM MẠCH (Bắt buộc)** - **Lợi ích**: Bác sĩ sẽ làm các xét nghiệm (điện tâm đồ, siêu âm tim, test gắng sức...) để*
- *ng cần phải đến bệnh viện ngay trong đêm nay**, nhưng Bác **CẦN ĐẶT LỊCH KHÁM CHUYÊN KHOA TIM MẠCH TRONG 1-2 NGÀY TỚI** (không nên để chậm hơn 1 tuần).*

### NETTING — 69× — suggested: `SPELL`
- ***Điều trị**: Tùy chẩn đoán, có thể dùng thuốc hoặc cần can thiệp chuyên sâu hơn **SAFETY NETTING (LƯU Ý AN TOÀN):** Anh Hùng à, nếu trong thời gian chờ đi khám, anh xuất hiện **đa*
- ***AN TOÀN (SAFETY NETTING):** Nếu trong thời gian chờ đi khám, Lan thấy xuất hiện các dấu hiệu như: sưng đau da đầu, sốt, hoặc rụng tóc*
- *u hóa hoặc Gan mật để được siêu âm và xét nghiệm - KHÔNG tự điều trị tại nhà --- **SAFETY NETTING (Các dấu hiệu cần đi cấp cứu ngay):** Nếu Bác thấy bất kỳ dấu hiệu nào sau đây, ***

### BPH — 69× — suggested: `SPELL`
- *- Tiền sử: HTN, DM, BPH.*
- ***Phì đại tuyến tiền liệt (BPH)** là tình trạng tuyến tiền liệt (một tuyến ở nam giới, nằm dưới bàng quang, bao quanh niệu đạo) tăng kích th*
- ***BPH là bệnh của người lớn tuổi**: Thường gặp ở nam giới trên 50-60 tuổi.*

### AMD — 69× — suggested: `SPELL`
- *g mất thị lực ngoại vi trước, có thể không đau (chronic glaucoma) - Thoái hóa hoàng điểm (AMD): mờ trung tâm, nhìn méo - Vấn đề khúc xạ: cần điều chỉnh kính - Patient đã đi khám và*
- ***Thoái hóa hoàng điểm tuổi già (AMD)**: Đây là nguyên nhân phổ biến ở người trên82 tuổi, gây mờ mắt trung tâm và nhìn méo hình 2.*
- *Tôi sẽ giải thích ngắn gọn cho bác hiểu: **Bệnh thoái hóa hoàng điểm tuổi già (AMD)**: Là tình trạng điểm vàng ở đáy mắt (chỗ nhìn tinh nhất) bị tổn thương.*

### ACL — 68× — suggested: `SPELL`
- *lỏng lẻo**: Dấu hiệu quan trọng gợi ý tổn thương dây chằng (ví dụ: dây chằng chéo trước - ACL).*
- *lỏng" và không chịu được weight làm bác sĩ lo lắng về khả năng đứt dây chằng chéo trước (ACL) - một chấn thương thường gặp ở trẻ em chơi thể thao.*
- ***Rách dây chằng** (như em lo lắng - ACL hoặc MCL) 3.*

### PCR — 67× — suggested: `SPELL`
- *đánh giá nhiễm trùng - Chụp X-quang phổi nếu nghi ngờ viêm phổi - Cấy đờm hoặc xét nghiệm PCR để xác định vi khuẩn/phế cầu khuẩn nếu cần - **Điều trị**: Nếu là viêm phổi do phế cầu*
- *Nếu test dương tính hoặc triệu chứng nặng hơn, em nên đi khám để được làm thêm xét nghiệm PCR nếu cần.*
- *- **Xét nghiệm cần làm**: Bác sĩ sẽ lấy dịch/nhọt tại vết thương để xét nghiệm PCR hoặc nuôi cấy virus, và có thể làm xét nghiệm máu để kiểm tra kháng thể.*

### OA — 66× — suggested: `SPELL`
- ***Thoái hóa cột sống (OA)**: Phù hợp tuổi 62, đau tăng khi vận động, giảm nghỉ 3.*
- ***Thoái hóa cột sống (OA)**: Phù hợp tuổi 62, do lão hóa, đau tăng khi vận động, giảm nghỉ 3.*
- *Cứng khớp < 30 phút thường gợi ý viêm xương khớp (OA), trong khi > 30-60 phút gợi ý viêm khớp dạng thấp (RA) hoặc các bệnh viêm khớp khác.*

### IT — 66× — suggested: `SPELL`
- *Em đang học để thi chứng chỉ IT, áp lực lắm ạ.*
- *- Bệnh nhân 33 tuổi, nam, làm IT (Systems Analyst).*
- *Con chỉ là nhân viên IT bình thường, thu nhập cũng vừa phải nên cũng lo lắng về chi phí ạ.*

### CLINICAL — 66× — suggested: `STRIP`
- ***CLINICAL LOGIC**: - Triệu chứng: Đau lưng giữa + tê hai bên mạng sườn.*
- ***CLINICAL LOGIC**: - Patient wants to know typical duration of viral pharyngitis - This is general health information I*
- ***CLINICAL LOGIC**: Đây là câu hỏi thực tế và hợp lý.*

### ARB — 65× — suggested: `SPELL`
- *- **Cao huyết áp**: Cần lưu ý thuốc đang dùng (thường là lợi tiểu, ức chế ACE/ARB) có thể gây tác dụng phụ, nhưng không giải thích rõ ràng toàn bộ picture (sốt, sút cân, đau họng).*
- *đơn thuốc** để được xem xét đổi sang thuốc điều trị cao huyết áp khác (ví dụ: thuốc nhóm ARB như Losartan, Valsartan) mà không gây ho.*
- ***Cung cấp lựa chọn** (2-3 options): - Option 1: Đổi sang thuốc huyết áp nhóm ARB (Irbesartan/Valsartan) - ít gây ho.*

### PA — 64× — suggested: `SPELL`
- */kem mỏng, oil-free, không gây bít tắc lỗ chân lông (non-comedogenic) - Chỉ số SPF 30-50, PA+++ trở lên - Tìm chữ "oil-free" hoặc "dành cho da dầu" **Cách dùng**: - Dùng **MỖI NGÀY*
- ***Công nghệ mới**: Nên chọn loại có ghi "Broad Spectrum" hoặc PA+++ để bảo vệ khỏi cả tia UVA (gây lão hóa) và UVB (gây cháy nắng).*
- *Em nên chọn loại có SPF 50+, PA++++, và ghi rõ "Physical Sunscreen" hoặc "Mineral Sunscreen".*

### FODMAP — 63× — suggested: `SPELL`
- *Thử giảm các thực phẩm giàu FODMAP**: Đây là nhóm carbohydrate khó tiêu hóa, có thể gây đầy hơi và đau bụng.*
- ***Tóm tắt kế hoạch:** - Ghi nhật ký triệu chứng và điều chỉnh chế độ ăn uống (Low FODMAP, hạn chế thức ăn kích ứng) - Quản lý stress và nghỉ ngơi đủ - Đi khám bác sĩ chuyên khoa Ti*
- *giúp cải thiện triệu chứng: **Về chế độ ăn uống:** - Anh có thể thử áp dụng chế độ ăn Low FODMAP: hạn chế các loại thực phẩm nhiều đường và tinh bột khó tiêu hóa như sữa, lúa mì, m*

### CAO — 62× — suggested: `SPELL`
- ***Huyết áp cao không kiểm soát**: Chỉ số 145/95 mmHg của Anh cách đây 1 tháng là CAO, và việc Anh không uống thuốc đều đặn khiến tình trạng này kéo dài.*
- ***Lưu ý**: Nếu chân tê, đau hơn, hoặc sưng nhiều hơn → Tháo băng ra ngay **NÂNG CAO CHÂN**: Khi nằm hoặc nghỉ, kê chân lên gối cao hơn tim một chút Em có hiểu từng bước này không ạ*
- *(sau vài tuần) - **Ưu điểm**: Không ảnh hưởng công việc hiện tại - **Nhược điểm**: RỦI RO CAO - triệu chứng có thể nặng thêm, có thể dẫn đến nhồi máu cơ tim cấp tính **Lựa chọn 3***

### DCIS — 61× — suggested: `SPELL`
- *Đây là mục tiêu hoàn toàn khả thi với DCIS giai đoạn sớm.*
- ***Trước hết, Bác đã nghe qua về DCIS và tại sao bác sĩ lại đề nghị phẫu thuật chưa ạ?** **Về thắc mắc của Bác, tôi xin chia sẻ như sau:** DCIS là*
- *bác sĩ lại đề nghị phẫu thuật chưa ạ?** **Về thắc mắc của Bác, tôi xin chia sẻ như sau:** DCIS là ung thư giai đoạn 0, các tế bào ung thư chỉ nằm trong ống dẫn sữa chưa xâm lấn ra *

### XE — 59× — suggested: `SPELL`
- *Anh/Chị tuyệt đối **KHÔNG TỰ LÁI XE** nữa nhé.*
- *Tôi cần trả lời **rất rõ ràng**: **TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ LÁI XE SAU KHI DÙNG EPIPEN HOẶC KHI ĐANG CÓ PHẢN ỨNG DỊ ỨNG.** **Lý do c cực kỳ nguy hiểm:** 1.*
- *115 ngay → **thông báo "dị ứng nặng, cần xe cấp cứu"** - Tự tiêm EpiPen (nếu có) - **ĐỢI XE CẤP CỨU ĐẾN** - KHÔNG được tự lái xe hay đi taxi tự lái **Nếu bác thực sự ở một mình và *

### VSD — 59× — suggested: `SPELL`
- ***Tóm tắt những gì anh mô tả:** - Tiền sử thông liên thất (VSD) từ nhỏ, đã tự đóng lại - Khó thở, tim đập nhanh, nặng ngực khi leo 2-3 tầng cầu thang hoặc đi bộ nhanh - Cảm*
- *Siêu âm tim để kiểm tra chức năng tim và cấu trúc (đặc biệt với tiền sử VSD) 4.*
- *Anh có tiền sử thông liên thất (VSD) từ nhỏ, may là không cần phẫu thuật.*

### INITIATING — 58× — suggested: `SPELL`
- *[[INITIATING]]*
- *<think> **PHASE CHECK**: Turn 2 - Still in INITIATING THE SESSION, transitioning to GATHERING INFORMATION.*
- *Let me write it properly: <think> Tôi đang ở PHASE 1: INITIATING THE SESSION (Turn 1).*

### SAO — 57× — suggested: `SPELL`
- *Tôi xin giải thích rõ: **Tại SAO bác vẫn nên đi nội soi đại tràng dù triệu chứng có cải thiện?** Vì bác đã **50 tuổi** - đây là độ tuổi **bắt*
- ***Về việc tập luyện khi bận:** **HOÀN TOÀN KHÔ SAO cả!** Quan trọng là **tính nhất quán**, không phải mỗi ngày.*
- ***TẠI SAO EM CẢM THẤY NHƯ VẬY?** Não bộ em hiện tại đang trong tình trạng "overloaded" - giống như RAM máy tính đầy, kh*

### FV — 56× — suggested: `SPELL`
- *- **Bệnh viện FV** hoặc **Bệnh viện Tâm Anh** (nếu muốn khám dịch vụ nhanh hơn).*
- *- **Bệnh viện tư (như Vinmec, Hoàn Mỹ, FV Hospital...)**: Ưu điểm là dịch vụ tốt, ít chờ đợi, tiện nghi hiện đại.*
- *TP.HCM** (số 280 Điện Biên Phủ, Q.3) - chuyên khoa mắt hàng đầu - **Khoa Mắt - Bệnh viện FV** (số 6 Nguyễn Lương Bằng, Q.7) - Các phòng khám chuyên khoa mắt uy tín gần nhà **Lưu ý *

### RSI — 55× — suggested: `SPELL`
- ***Trước tiên, chị có biết gì về hội chứng đau cơ xương do tư thế làm việc (còn gọi là RSI - Repetitive Strain Injury) chưa?** Nếu chưa, tôi sẽ giải thích ngắn gọn: Triệu chứng của *
- *những gì chị mô tả, tôi nghi ngờ tình trạng của chị có thể do **chấn thương do lặp lại** (RSI) hoặc **viêm gân do thoa** do tính chất công việc gõ máy tính nhiều và ít nghỉ ngơi.*
- *: Dựa trên những gì em mô tả, đây có thể là tình trạng "chấn thương do thao tác lặp lại" (RSI) do gõ phím và bưng bê nhiều.*

### DA — 54× — suggested: `SPELL`
- *VỀ KEM CHỐNG NẮNG CHO DA DẦU** **Loại phù hợp**: - Chọn kem chống nắng vật lý lai hóa học hoặc hóa học - Dạng lotion/kem mỏng, oil-fre*
- *DA DẦU NHƯNG MÁ KHÔ - CÓ PHẢI DA THIẾU NƯỚC KHÔNG?** Đúng vậy!*
- *CÁCH DÙNG KEM DƯỠNG ẨM CHO DA HỖN HỢP** Anh nên **thoa cả mặt**, nhưng điều chỉnh lượng: - **Vùng chữ T (trán, mũi, cằm)**: Thoa một lớp mỏ*

### CBT — 54× — suggested: `SPELL`
- *Bác sĩ tâm lý sẽ: * **Dùng liệu pháp nhận thức - hành vi (CBT)**: Giúp anh/chị thay đổi cách suy nghĩ về những căng thẳng (công việc, ở một mình), từ đó não không phát ra*
- *trẻ em thường là **trò chơi trị liệu (play therapy)** hoặc **trị liệu nhận thức-hành vi (CBT) đơn giản** - Đây là phương pháp an toàn, không dùng thuốc, giúp bé xử lý nỗi sợ một cá*
- *hoặc thuốc điều hòa giấc ngủ trong một số trường hợp nặng - Liệu pháp hành vi nhận thức (CBT-I) cho insomnia/stress - Kiểm tra các bệnh lý nền (ngưng thở khi ngủ, động kinh...) **V*

### PCP — 54× — suggested: `SPELL`
- ***Nhờ bác sĩ gia đình (Primary Care Physician - PCP)**: Nếu em có bác sĩ gia đình quen, hãy đặt lịch khám và nhờ họ giới thiệu đến bác sĩ chuyên khoa Cơ xương kh*
- *Với Medicare và Medicaid, bác có thể tìm PCP qua các cách sau: **Tìm PCP gần nhà:** - Gọi **Medicaid**: 1-800-541-5555 (California Medi-Cal) để được cung*
- *Với Medicare và Medicaid, bác có thể tìm PCP qua các cách sau: **Tìm PCP gần nhà:** - Gọi **Medicaid**: 1-800-541-5555 (California Medi-Cal) để được cung cấp danh sách PCP trong mạ*

### MUA — 51× — suggested: `SPELL`
- ***EM CẦN NGHE KỸ NÀY**: Em **TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ MUA KHÁNG SINH UỐNG** nhé!*
- *VỀ VIỆC MUA THUỐC:** Tôi **KHÔNG THỂ** tư vấn cho anh mua thuốc cụ thể hay liều lượng nào.*
- ***Quan trọng nhất**: Bác **KHÔNG NÊN TỰ MUA THUỐC KHÁC** như thuốc kháng viêm (Ibuprofen, Diclofenac) hay thuốc giảm đau mạnh hơn mà không có chỉ định củ*

### ERCP — 50× — suggested: `SPELL`
- ***Nội soi đường mật (ERCP) hoặc sinh thiết gan**: Chỉ cần làm nếu xét nghiệm máu và siêu âm chưa rõ ràng, hoặc nghi ngờ có sán trong đư*
- ***Nội soi lấy sỏi (ERCP)**: Thường dùng cho sỏi đã gây tắc ống mật chủ, không phải để lấy sỏi trong túi mật.*
- ***Nội soi lấy sỏi (ERCP)**: Dùng cho trường hợp sỏi đã rơi xuống ống mật chủ gây tắc, không phải để lấy sỏi trong túi mật.*

### CUNG — 50× — suggested: `SPELL`
- ***TÓM TẮT THÔNG TIN BÁC CUNG CẤP:** - **Vấn đề chính**: Đau khuỷu tay phải - **Thời gian**: Khoảng 2 tuần nay - **Nguyên nhân**: Sau khi d*
- *c sĩ sẽ tư vấn chi tiết về chi phí, phẫu thuật nếu cần, và chế độ ăn uống cụ thể **TÔI ĐÃ CUNG CẤP ĐẦY ĐỦ THÔNG TIN CẦN THIẾT CHO VIỆC ĐI KHÁM.*
- ***THÔNG TIN CẦN CUNG CẤP**: - Giải thích quy trình khám một cách đơn giản, dễ hiểu cho trẻ 8 tuổi - Giúp bé chuẩn bị tâm lý - Trấn*

### DINH — 48× — suggested: `SPELL`
- ***Massage**: Mỗi tối, dùng đầu ngón tay massage nhẹ nhàng theo vòng tròn trong 2-3 phút **DINH DƯỠNG TỐT CHO DA TỪ BÊN TRONG:** - **Uống đủ nước**: 1.5-2 lít nước/ngày - **Ăn nhiều*
- *ờng: chuối, táo (bỏ vỏ), lê - Sữa chua không đường - Uống đủ 2-2.5 lít nước/ngày **VỀ HỌC DINH DƯỠNG:** Bác có thể tìm hiểu từ các nguồn uy tín như: - Viện Dinh dưỡng Quốc gia (có *
- ***VỀ DINH DƯỠNG TỐT CHO KHỚP (Anh có thể áp dụng ngay):** **Nên ăn:** - **Cá béo**: Cá hồi, cá thu, cá trích (giàu Omeg*

### HSV — 48× — suggested: `SPELL`
- *s sinh dục** (mụn rộp sinh dục), một bệnh lây qua đường tình dục do virus herpes simplex (HSV) gây ra.*
- ***Herpes sinh dục là một bệnh lây truyền qua đường tình dục do virus herpes simplex (HSV) gây ra.** Triệu chứng điển hình chính là những mụn nước nhỏ như anh mô tả, sau đó vỡ ra tạ*
- *hoàn toàn**, nhưng tôi cần giải thích rõ hơn để Anh/Chị yên tâm: **Herpes simplex virus (HSV)** một khi đã nhiễm vào cơ thể sẽ sống trong hệ thần kinh và không thể tiêu diệt hoàn t*

### QUY — 44× — suggested: `SPELL`
- *QUY TRÌNH SKINCARE CƠ BẢN 3 BƯỚC (Sáng & Tối)** **Bước 1: Làm sạch (Cleansing)** - Sáng: Rửa mặt bằng sữa rửa mặt*
- *y trang) massage trên da khô - **Bước 2**: Rửa lại bằng sữa rửa mặt dịu nhẹ --- **TÓM LẠI QUY TRÌNH TỐI CHO ANH**: 1.*
- *đi bộ 10-15 phút mỗi ngày trong nhà hoặc sân - Giúp tăng tuần hoàn, giảm mệt mỏi **⚠️ CÁC QUY TẮC AN TOÀN BÁC CẦN NHỚ:** - **Bắt đầu chậm**: Tập nhẹ nhàng, nếu đau tăng thì dừng ng*

### BNP — 43× — suggested: `SPELL`
- ***Xét nghiệm máu**: Đánh giá chức năng thận, điện giải, men tim, BNP (chỉ số suy tim) 2.*
- *tiền sử bệnh tim**: - **Xét nghiệm máu**: Đánh giá chức năng thận, điện giải, chỉ số tim (BNP/NT-proBNP - đánh giá suy tim).*
- *Về xét nghiệm: ECG, siêu âm tim, xét nghiệm máu (troponin, BNP), có thể cần MRI 2.*

### CTS — 43× — suggested: `SPELL`
- *như sau: **Chẩn đoán sơ bộ**: Triệu chứng của em rất phù hợp với **hội chứng ống cổ tay (CTS)** - tình trạng thần kinh giữa bị chèn ép ở cổ tay, hoặc **viêm gân De Quervain** - viê*
- ***cột sống cổ** (cervical spine) hoặc **hội chứng ống cổ tay** (Carpal Tunnel Syndrome - CTS) kết hợp với **đau đầu do căng thẳng**.*
- *ên quan đến tư thế hoặc chấn thương do lặp lại động tác (RSI), hoặc hội chứng ống cổ tay (CTS).*

### CON — 43× — suggested: `SPELL`
- *Bác sĩ chuyên khoa sẽ thăm khám kỹ và có thể chỉ định xét nghiệm --- **LƯU Ý AN TOÀN CỦA CON:** Bác cần đi khám ngay nếu: - Triệu chứng tê tăng nặng dữ dội - Xuất hiện yếu chân khô*
- *yếu chân không kiểm soát được - Có đau lưng lan xuống chân - Có rối loạn đại tiểu tiện **CON KHÔNG THỂ CHẨN ĐOÁN HOẶC KÊ ĐƠN THUỐC ĐƯỢC Ạ.** Thông tin trên chỉ mang tính tham khảo.*
- *Dựa trên những gì Bác chia sẻ, con xin giải thích và tư vấn như sau: **TRƯỚC KHI CON GIẢI THÍCH, BÁC CÓ BIẾT GÌ VỀ "BỆNH MẠCH VÀNH" HAY "ĐAU THẮT NGỰC" KHÔNG Ạ?** Nếu Bác chưa rõ, *

### SLE — 42× — suggested: `SPELL`
- *This is **Keratoconjunctivitis Sicca** (Dry eyes), common in Sjogren's syndrome or SLE, but also seen in APS.*
- *Mệt mỏi kéo dài, gầy sút Đây là những dấu hiệu đặc trưng của bệnh lupus ban đỏ hệ thống (SLE) - một bệnh tự miễn hệ thống.*
- *dấu hiệu đặc trưng của bệnh tự miễn, đặc biệt có thể liên quan đến lupus ban đỏ hệ thống (SLE).*

### ASK — 41× — suggested: `SPELL`
- ***ASK - TELL - ASK**: Bác có biết gì về hội chứng ruột kích thích này chưa ạ?*
- ***[ASK]** Tôi giải thích vậy em có hiểu không?*
- ***[ASK]** Dựa trên những gì em mô tả, Tôi nghi ngờ em đang gặp tình trạng **huyết áp thấp tư thế** - tức là huyết áp*

### RFA — 40× — suggested: `SPELL`
- *i đoạn phát hiện: - **Giai đoạn sớm**: Có thể phẫu thuật cắt bỏ khối u, đốt sóng cao tần (RFA), hoặc ghép gan.*
- *- **Đốt sóng cao tần (RFA)**: Dùng nhiệt để tiêu diệt tế bào ung thư.*
- *Về phương pháp điều trị, bác sĩ đã đề cập đến phẫu thuật hoặc đốt sóng cao tần (RFA) - đây là những phương pháp điều trị triệt để cho ung thư gan giai đoạn đầu.*

### CO2 — 40× — suggested: `SPELL`
- *Điều này khiến lượng khí CO2 trong máu thay đổi, gây ra cảm giác ngứa ran, tê bì ở tay chân.*
- *Anh/Chị lo lắng nhiều về mặt thẩm mỹ, vẫn có một số phương pháp can thiệp như dùng laser CO2, đốt điện hay peel da...*
- *Các phương pháp: Laser CO2, đốt điện, bôi acid...*

### ED — 40× — suggested: `SPELL`
- ***Về thuốc hỗ trợ:** Cháu hiểu bác muốn dùng thuốc, nhưng bác cần lưu ý: - Thuốc hỗ trợ ED (như Viagra, Cialis...) có thể ảnh hưởng đến tim mạch.*
- *sleep apnea**: Ngáy to là dấu hiệu quan trọng của sleep apnea - nguyên nhân phổ biến gây ED do giảm testosterone và oxy máu về đêm.*
- *Nếu anh có bất kỳ dấu hiệu nào như đau ngực, khó thở đột ngột, hay ED trở nên nghiêm trọng hơn, hãy đến bệnh viện ngay nhé.*

### HR — 39× — suggested: `SPELL`
- *sang làm việc bán thời gian** hoặc làm việc từ xa nếu công ty cho phép - **Trò chuyện với HR** (phòng nhân sự) của công ty đểhiểu về quyền lợi nghỉ ốm **Về chi phí:** Bác nên h hỏi*
- *Em đang làm HR manager, công việc cũng bận rộn, em sợ việc điều trị sẽ ảnh hưởng đến công việc.*
- *Tôi là Nguyễn Văn Tài, 27 tuổi, đang làm nhân viên HR.*

### START — 39× — suggested: `SPELL`
- *[[START]]*
- *[[EMBEDDED_CONVERSATION_START]]*
- *``` [[START]] ```*

### RED — 39× — suggested: `SPELL`
- *- Khả năng cao: Viêm khớp nhiễm trùng (septic arthritis) hoặc viêm khớp cấp tính khác - **RED FLAG**: Đau dữ dội, sưng đỏ nóng, không có chấn thương - cần loại trừ nhiễm trùng **Sa*
- *Nuốt nghẹn với tất cả thức ăn (đặc biệt cơm) - RED FLAG 2.*
- *Sút 3kg trong 2 tháng - RED FLAG 3.*

### FT4 — 39× — suggested: `SPELL`
- ***Kiểm tra tuyến giáp**: Vì bác dễ nóng tính hơn, nên xét nghiệm TSH, FT4 Bác nghĩ sao ạ?*
- *Bạn có nhớ kết quả xét nghiệm TSH, FT3, FT4 gần nhất không?*
- *bạn nên làm gì:** - Đi tái khám đúng hẹn (sau 2 tháng) để xét nghiệm lại chỉ số TSH, FT3, FT4.*

### IBD — 39× — suggested: `SPELL`
- ***Viêm ruột mạn (IBD)**: Ít khả năng hơn vì không có máu, không sút cân.*
- ***Viêm loét đại tràng (IBD)**: Đây là bệnh mạn tính, nhưng có thể bùng phát sau đợt nhiễm trùng hoặc do di truyền.*
- *- *Viêm loét đại tràng (IBD)*: Là bệnh mạn tính, **không thể chữa khỏi hoàn toàn**, nhưng có thể kiểm soát tốt bằng thuốc.*

### ITP — 39× — suggested: `SPELL`
- *không có bệnh nền, không thuốc -> Cần nghĩ đến **Ban xuất huyết giảm tiểu cầu miễn dịch (ITP)** hoặc các bệnh lý đông máu khác.*
- *- Có sốt, mệt mỏi không (dấu hiệu nhiễm trùng virus - nguyên nhân phổ biến gây ITP).*
- ***, nhưng dựa vào đặc điểm này, đây có thể là tình trạng gọi là "giảm tiểu cầu tạm thời" (ITP).*

### JIA — 38× — suggested: `SPELL`
- *thăm khám trực tiếp** để loại trừ các bệnh lý mạn tính như viêm khớp tự miễn thiếu niên (JIA) hoặc các bệnh tự miễn khác.*
- *là dấu hiệu kinh điển của viêm khớp mạn tính, đặc biệt là **Viêm khớp tự miễn thiếu niên (JIA)** type viêm khớp (oligoarticular hoặc polyarticular).*
- *- **Tuổi:** 4 tuổi là độ tuổi hay gặp JIA.*

### NST — 37× — suggested: `SPELL`
- *- **Xét nghiệm Karyotype (chụp NST)**: Nếu bác sĩ nghi ngờ có bất thường NST tiềm ẩn trong gia đình, bác sĩ có thể đề nghị em làm xét nghiệm máu*
- *- **Xét nghiệm Karyotype (chụp NST)**: Nếu bác sĩ nghi ngờ có bất thường NST tiềm ẩn trong gia đình, bác sĩ có thể đề nghị em làm xét nghiệm máu này để kiểm tra NST của em.*
- *g NST tiềm ẩn trong gia đình, bác sĩ có thể đề nghị em làm xét nghiệm máu này để kiểm tra NST của em.*

### EKG — 37× — suggested: `SPELL`
- *Về câu hỏi của bác: "QRS rộng" là thuật ngữ chỉ một phần trên điện tâm đồ (EKG), nó thường liên quan đến cách nhịp tim hoạt động hoặc có thể do ảnh hưởng của thuốc hoặc một số bệnh*
- *lock phân nhánh" (Branching Block) thực ra là một thuật ngữ chuyên sâu trong điện tâm đồ (EKG) về nhịp tim, hoặc trong lập trình tin học, chứ không phải là phương pháp điều trị hay*
- ***Đo điện tâm đồ (ECG/EKG)**: - Gắn các điện cực lên ngực, tay, chân - Ghi lại hoạt động điện của tim - Xong trong 5-10 phút, chi phí t*

### II — 36× — suggested: `SPELL`
- ***Về collagen type II**: Đây là thực phẩm chức năng, thường không cần toa bác sĩ, nhưng tôi khuyên chị nên: - Mua ở hiệu thuốc uy t*
- *teroid (NSAIDs) hoặc thuốc điều trị triệu chứng chậm tác dụng (glucosamine, collagen type II).*
- *i Bệnh viện Tai Mũi Họng Trung ương, bác có thể yêu cầu đặt lịch với **bác sĩ chuyên khoa II hoặc bác sĩ trưởng khoa** - những người có nhiều kinh nghiệm - Bác có thể hỏi trực tiếp*

### DANH — 36× — suggested: `SPELL`
- ***DANH SÁCH TRIỆU CHỨNG CHO BÁC SĨ** **1.*
- *Wait, the prompt says "DANH TÍNH & VIỆT HÓA (BẮT BUỘC): Bạn PHẢI chọn một cái tên thuần Việt".*
- *- The prompt says "DANH TÍNH & VIỆT HÓA (BẮT BUỘC): Bạn PHẢI chọn một cái tên thuần Việt".*

### MBA — 36× — suggested: `SPELL`
- *Tôi cũng đang có kế hoạch thi MBA và muốn được tư vấn thêm về cách giảm stress để có thể làm việc hiệu quả hơn.*
- *Chúc anh sớm cải thiện sức khỏe, thi MBA thành công và giảm stress hiệu quả!*
- ***Về giảm stress và kế hoạch thi MBA:** Đây là điều anh nên tập trung vì stress là nguyên nhân chính gây triệu chứng hiện tại.*

### BS — 36× — suggested: `SPELL`
- *ông cần kiêng đồ gì **Tóm tắt kế hoạch:** - Bác sẽ đi khám Da liễu hoặc Ngoại tổng quát - BS sẽ vệ sinh rốn, kê thuốc và hướng dẫn chăm sóc - Không cần phẫu thuật, chỉ dùng thuốc **
- *Các phòng khám da liễu tư nhân uy tín**: Như phòng khám của PGS.TS.BS da liễu tại các bệnh viện lớn **Lưu ý cho Bác**: - Nên đặt lịch khám trước để không phải chờ đợi lâu - Mang t*
- *Với tình trạng của bác,BS gia đình sẽ là người đánh giá tổng quát và điều chỉnh thuốc huyết áp phù hợp nhất.*

### TPCN — 36× — suggested: `SPELL`
- *(Thuốc giảm đau, kháng sinh, TPCN...).*
- ***Về thảo dược và thực phẩm chức năng (TPCN)**: Lan cần **cẩn trọng** vì: - Hiệu quả chưa được chứng minh rõ ràng qua nghiên cứu lâm sàng.*
- ***Lời khuyên của tôi**: Nếu Lan muốn dùng bất kỳ loại thảo dược hay TPCN nào, **hãy hỏi ý kiến bác sĩ chuyên khoa trước khi dùng**.*

### INR — 35× — suggested: `SPELL`
- *răng) để bác sĩ cân nhắc nguy cơ chảy máu và có thể yêu cầu Bác kiểm tra chỉ số đông máu (INR) trước.*
- ***Theo dõi chỉ số INR**: Bác cần đi xét nghiệm máu (INR) định kỳ theo lịch hẹn của bác sĩ.*
- *Nếu chỉ số INR không ổn định, bác sĩ sẽ điều chỉnh liều Warfarin hoặc dặn dò bác điều chỉnh lượng rau ăn vào.*

### AFP — 35× — suggested: `SPELL`
- *n và làm thêm xét nghiệm chuyên sâu** - Bác cần quay lại bệnh viện để làm thêm xét nghiệm AFP (chỉ số ung thư gan), sinh thiết khối u (nếu bác sĩ chỉ định), và chụp CT scan hoặc MR*
- *Kết quả xét nghiệm máu cụ thể như thế nào (ví dụ như AFP - chỉ số ung thư gan)?*
- *Xét nghiệm máu: chức năng gan, men gan, marker ung thư gan (AFP), xét nghiệm virus gan 3.*

### LPR — 35× — suggested: `SPELL`
- *ực quản (GERD)**, và biến chứng lên họng gọi là **trào ngược dạ dày thực quản thanh quản (LPR)**.*
- *h trạng này có thể do hai nguyên nhân kết hợp: - **Trào ngược dạ dày thực quản thầm lặng (LPR)**: Đắng miệng ban đêm, khô cổ họng, cảm giác có đờm là dấu hiệu điển hình.*
- *ể chia sẻ một vài khả năng có thể: **Khả năng cao nhất** là **trào ngược acid thanh quản (LPR)** - tức là acid dạ dày trào lên ảnh hưởng đến dây thanh quản.*

### D3 — 35× — suggested: `SPELL`
- *Vitamin D**: - Anh/chị có thể tự mua ở hiệu thuốc: Nên chọn loại **Canxi kết hợp Vitamin D3** (ví dụ: Canxi carbonate + D3, hoặc Canxi citrate + D3).*
- *tự mua ở hiệu thuốc: Nên chọn loại **Canxi kết hợp Vitamin D3** (ví dụ: Canxi carbonate + D3, hoặc Canxi citrate + D3).*
- *chọn loại **Canxi kết hợp Vitamin D3** (ví dụ: Canxi carbonate + D3, hoặc Canxi citrate + D3).*

### KEM — 34× — suggested: `SPELL`
- *VỀ KEM CHỐNG NẮNG CHO DA DẦU** **Loại phù hợp**: - Chọn kem chống nắng vật lý lai hóa học hoặc hóa học - Dạng lotion*
- *CÁCH DÙNG KEM DƯỠNG ẨM CHO DA HỖN HỢP** Anh nên **thoa cả mặt**, nhưng điều chỉnh lượng: - **Vùng chữ T (trán, mũi, cằm)**:*
- *KEM CHỐNG NẮNG - CÓ CẦN TẨY TRANG KHÔNG?** **CÓ!** Kem chống nắng (kể cả không trang điểm) cần được **tẩy trang k*

### MANG — 34× — suggested: `SPELL`
- *Đây là checklist em nên chuẩn bị: **📄 GIẤY TỜ CẦN MANG**: - Kết quả xét nghiệm, chẩn đoán cũ (em đã có rồi phải không?) - Đơn thuốc (nếu có) - Thẻ bảo hiểm y tế, CC*
- *TÀI LIỆU CẦN MANG THEO:** - Kết quả khám sức khỏe gần nhất (đặc biệt phần tim mạch) - Các xét nghiệm máu gần đây (nếu có) - Đơn*
- ***MANG THEO:** - Tất cả thuốc đang dùng (Aspirin, Clopidogrel, Atorvastatin, Metoprolol) - Giấy tờ liên quan đến việ*

### HBV — 34× — suggested: `SPELL`
- *nghiệm: công thức máu, chức năng gan (AST, ALT, bilirubin), định lượng virus viêm gan B (HBV DNA), và siêu âm gan **Lưu ý an toàn quan trọng**: Nếu anh/chị thấy: - Đau bụng dữ dội *
- *Em nghe nói có xét nghiệm HBeAg và HBV DNA là gì vậy?*
- *rị**, nên tôi **không thể** trả lời chính xác các câu hỏi về: - Xét nghiệm cụ thể (HBeAg, HBV DNA) - Thuốc điều trị, thời gian uống, tác dụng phụ - Chế độ ăn uống, tập luyện cụ thể*

### THE — 34× — suggested: `LOWERCASE` → `the`
- *Hãy nói như một bệnh nhân." **I AM THE PATIENT.** The AI is the patient.*
- *<thinking> **PHASE CHECK**: Tôi đang ở **PHASE 4: CLOSING THE SESSION**.*
- ***Phase Check**: Tôi đang ở **PHASE 3: BUILDING THE RELATIONSHIP & EXPLORING THE PATIENT'S PERSPECTIVE**.*

### CH — 34× — suggested: `SPELL`
- *DÙNG CHỈ NHA KHOA**: - **Thời gian**: 1 lần/ngày (tối trước khi đánh răng).*
- *CHẾ ĐỘ ĂN**: - Hạn chế đồ ngọt, nước có gas.*
- *THEO DÕI TRIỆU CHỨNG**: - Trong 1-2 tuần, nếu triệu chứng giảm (ít chảy máu, bớt đau) thì tiếp tục.*

### TESE — 34× — suggested: `SPELL`
- *ch đồ để kiểm tra có tinh trùng trở lại không **Về phương án lấy tinh trùng từ tinh hoàn (TESE):** Nếu phẫu thuật nối ống dẫn không thành công, bạn hoàn toàn có thể yên tâm vì có p*
- *u thuật nối ống dẫn không thành công, bạn hoàn toàn có thể yên tâm vì có phương án này: - TESE là **phẫu thuật nhỏ**, chỉ rạch một đường rất nhỏ ở bìu để lấy tinh trùng trực tiếp t*
- *trùng vẫn được tạo ra bình thường trong tinh hoàn, nên bác sĩ có thể lấy tinh trùng bằng TESE và làm IVF/ICSI luôn **Điều quan trọng nhất bạn cần làm ngay:** Hãy đặt lịch khám với *

### PMR — 33× — suggested: `SPELL`
- *Tôi sẽ giải thích sơ qua về **Polymyalgia Rheumatica (PMR)** để bác yên tâm: **Bệnh có nguy hiểm không?** - PMR không phải bệnh nan y, nhưng cần điều trị kịp thời để t*
- *sơ qua về **Polymyalgia Rheumatica (PMR)** để bác yên tâm: **Bệnh có nguy hiểm không?** - PMR không phải bệnh nan y, nhưng cần điều trị kịp thời để tránh biến chứng - Nếu không điề*
- *Nếu đúng là PMR thì đây là một bệnh viêm mạn tính thường gặp ở người trên 50 tuổi, gây đau và cơ bắp, đặc biệt là vùng vai, h*

### H2 — 33× — suggested: `SPELL`
- ***Khám bác sĩ**: Để được kê thuốc giảm acid nếu cần (thuốc kháng H2 hay ức chế bơm proton) **Lưu ý quan trọng**: Nếu bác có đau ngực dữ dội, khó thở, nôn ra máu, hay nuốt đau kh*
- *Tuy nhiên, bác sĩ có thể sẽ kê: - Thuốc giảm acid (như thuốc kháng H2 hay ức chế bơm proton) - Thuốc bảo vệ niêm mạc **Bác không nên tự mua thuốc uống**, vì cần bác sĩ đánh giá mứ*
- *Hoặc nhóm **H2 Blocker**.*

### TMD — 33× — suggested: `SPELL`
- ***Anh đã biết gì về "rối loạn khớp thái dương hàm" (TMD) chưa?** Nếu chưa, tôi có thể giải thích thêm để anh hiểu rõ hơn về tình trạng của mình.*
- *Em chưa biết nhiều về "rối loạn khớp thái dương hàm" (TMD) nên mong bác sĩ giải thích thêm cho em hiểu rõ hơn về tình trạng của mình ạ.*
- ***Rối loạn khớp thái dương hàm (TMD) là gì?** Khớp thái dương hàm là "bản lề" nằm ở hai bên tai, giúp em há-miệng và nhai.*

### ACTH — 33× — suggested: `SPELL`
- *Ngoài ra, anh nên đến bệnh viện để xét nghiệm các chỉ số sau: - **Cortisol và ACTH** (để kiểm tra tuyến thượng thận).*
- ***Tuyến thượng thận:** Cortisol, ACTH (để loại trừ suy tuyến thượng thận - Addison).*
- *Anh cần đến bệnh viện xét nghiệm **Cortisol, ACTH, TSH, Free T4** để chẩn đoán chính xác.*

### MMR — 33× — suggested: `SPELL`
- *ông thấy sưng tại chỗ, nhưng bé có thể bị đau nhức cơ hoặc mệt mỏi toàn thân sau mũi tiêm MMR, khiến bé cảm thấy khó chịu khi chịu lực ở chân.*
- *Anh có tiêm vắc-xin sởi - quai bị - Rubella (MMR) khi còn nhỏ không?*
- *nhà, (2) Đi khám bác sĩ để được thăm khám và xét nghiệm nếu cần, (3) Kiểm tra tiêm chủng MMR nếu không rõ.*

### GHI — 32× — suggested: `SPELL`
- *Bác có thể in ra hoặc ghi lại vào giấy note nhé: --- **BẢN GHI CHÚ TRƯỚC KHI ĐI KHÁM** **I.*
- *bản ghi chú ngắn gọn, bác có thể đọc to cho bác sĩ nghe hoặc đưa cho bác sĩ xem: --- **📌 GHI CHÚ CHO BÁC SĨ - BỆNH NHÂN NGUYỄN VĂN TÁM (82 TUỔI)** **1.*
- *- Đơn thuốc (nếu có) - Thẻ bảo hiểm y tế, CCCD - Giấy tờ tùy thân khác **📝 THÔNG TIN NÊN GHI CHÉP TRƯỚC**: 1.*

### HIIT — 32× — suggested: `SPELL`
- *Tập gym:** - **Nên tránh** các bài tập nặng như: nâng tạ nặng, cardio cường độ cao, HIIT - Em có thể tập **đi bộ nhẹ nhàng** hoặc yoga thư giãn - Tuyệt đối không cố gắng tập luyện *
- *- Tránh các bài tập cường độ cao quá gần giờ ngủ (như HIIT, chạy nước rút) vì có thể làm tăng nhịp tim và adrenaline, gây khó ngủ.*
- *- **Bài tập HIIT 7-10 phút**: Nhảy dây, squat, plank - làm ngay tại phòng khi nghỉ giải lao.*

### LASIK — 32× — suggested: `SPELL`
- *bé lớn**: Thường sau 18 tuổi, khi độ cận ổn định (không tăng trong 1-2 năm) - Phẫu thuật LASIK/PRK chỉ sửa độ cận, không "chữa khỏi" tật - nhưng sau mổ bé không cần đeo kính nữa - *
- ***Khô mắt sau mổ LASIK + hội chứng thị giác màn hình**: Mắt bị khô, cộm, khó chịu vì phải điều tiết nhiều khi nhìn gần Đây là tình t*
- *Trước đây tôi có bị cận thị nhưng đã mổ LASIK cách đây 5 năm rồi.*

### PAD — 32× — suggested: `SPELL`
- **: - **Thuốc**: - Cao huyết áp: Amlodipine 5mg → **OK**, calcium channel blocker, tốt cho PAD.*
- *lopidogrel** (antiplatelet) và **KHÔNG có statin** → **Đây là lỗ hổng lớn** trong quản lý PAD + DM + HTN.*
- ***Đánh giá chung**: - **Chẩn đoán lâm sàng**: **Peripheral Arterial Disease (PAD) nặng, Stage IIb** (claudication khoảng cách < 300m, nghỉ > 5 phút).*

### LO — 31× — suggested: `SPELL`
- *VỀ GIẢM LO ÂU:** - Dành 10-15 phút mỗi ngày để thư giãn (nghe nhạc, đi dạo, hít thở sâu) - Viết ra những điều lo lắng ra*
- *LOẠI DẦU GỘI PHÙ HỢP** **Tùy chọn an toàn nhất**: - **Dầu gội dịu nhẹ cho trẻ em**: Chọn loại không chứa sulfate*
- *- **Phân tích FIFE**: Em ấy **RẤT LO LẮNG** và đã tự tìm hiểu ("Em có nghe nói về bệnh suy tuyến yên...").*

### GIA — 31× — suggested: `SPELL`
- *ao nhiêu là đủ **Tóm lại**: Câu trả lời cho cả 2 câu hỏi của bác là: **HÃY ĐI KHÁM BÁC SĨ GIA ĐÌNH** để được tư vấn chính xác và an toàn nhất.*
- ***GỌI ĐIỆN CHO BÁC SĨ GIA ĐÌNH** để thông báo tình hình khẩn cấp.*
- *TIỀN SỬ GIA ĐÌNH:** - Không có ai trong gia đình bị ung thư --- Bác mang theo danh sách này hoặc đọc lại cho bác sĩ nghe*

### CA — 31× — suggested: `SPELL`
- *- **Xét nghiệm máu:** Kiểm tra chỉ số CA-125 (chỉ số ung thư, nhưng tăng cao trong lạc nội mạc).*
- ***Bác sĩ có thể sẽ chỉ định**: - Siêu âm đầu dò âm đạo - Xét nghiệm máu (CA-125) - Có thể cần MRI hoặc nội soi ổ bụng để chẩn đoán xác định **Anh có hiểu những thông tin này không *
- *Lives in Vietnam (adapted from Pomona, CA).*

### DEXA — 31× — suggested: `SPELL`
- *- Mang theo **kết quả xét nghiệm mật độ xương (DEXA)** cũ (nếu có).*
- *(Ví dụ như đo mật độ xương DEXA scan, hay xét nghiệm máu về canxi, vitamin D?), và bác sĩ có nói chỉ số cụ thể nào không?*
- *hoa Cột sống - Cơ xương khớp hoặc Nội tiết** để được chụp X-quang xương, đo mật độ xương (DEXA scan), và xét nghiệm máu (canxi, vitamin D, chức năng tuyến giáp, markers ung thư nếu*

### CPR — 31× — suggested: `SPELL`
- *Tôi đã được CPR và dùng máy khử rung ngay tại chỗ.*
- ***Học CPR**: Nếu anh chưa biết, đây là kỹ năng có thể cứu sống người khác 5.*
- ***Về người thân**: - Hỏi tiền sử bệnh gia đình - Khám sức khỏe định kỳ - Khuyến khích học CPR Tôi hy vọng những thông tin này giúp anh tự tin hơn trong hành trình phục hồi.*

### TELL — 30× — suggested: `SPELL`
- ***TELL:** Amlodipine 10mg có thể gây chóng mặt, tim đập nhanh hơn 5mg, nhưng nếu bác tự ý giảm liều thì huyết áp có*
- ***ASK - TELL - ASK**: Bác có biết gì về hội chứng ruột kích thích này chưa ạ?*
- ***Trước đây em có biết gì về tình trạng này chưa?** **[TELL]** Dựa trên những gì em chia sẻ, có một vài khả năng có thể giải thích tại sao em hay mệt và khó thở khi tập*

### HEPA — 30× — suggested: `SPELL`
- *Cách dùng máy lọc không khí hiệu quả:** - **Chọn máy có lọc HEPA**: Đây là loại màng lọc tốt nhất để giữ lại bụi mịn, phấn hoa, lông thú cưng.*
- ***Về máy lọc không khí:** Máy lọc không khí có thể giúp ích nếu bác chọn loại có bộ lọc HEPA, sẽ giữ lại bụi và phấn hoa.*
- *- Máy lọc không khí: Chọn loại có bộ lọc HEPA để lọc bụi và phấn hoa.*

### L5 — 30× — suggested: `SPELL`
- *tình trạng tê bì và yếu cơ chân trái của bác, nguyên nhân có thể do chèn ép rễ thần kinh L5.*
- *Triệu chứng này có thể do chèn ép rễ thần kinh L5.*
- *ch thông tin**: - **Triệu chứng**: Tê bì mặt ngoài đùi xuống cẳng chân (dạng rễ thần kinh L5).*

### RHM — 29× — suggested: `SPELL`
- *Chị Mai nên đi khám chuyên khoa **Răng Hàm Mặt (RHM)** trước tiên để kiểm tra khớp cắn và cấu trúc hàm.*
- *Nếu bác sĩ RHM xác định nguyên nhân chính do cơ và tư thế, họ có thể giới thiệu chị sang chuyên khoa **Cơ xương khớp** hoặc*
- ***Các địa điểm uy tín chị có thể tham khảo**: - Khoa RHM tại các bệnh viện lớn như Bệnh viện Đại học Y Dược, Bệnh viện Chợ Rẫy (TP.HCM) hoặc Bệnh viện Bạch Mai, Bệnh*

### NGHE — 28× — suggested: `SPELL`
- ***EM CẦN NGHE KỸ NÀY**: Em **TUYỆT ĐỐI KHÔNG ĐƯỢC TỰ MUA KHÁNG SINH UỐNG** nhé!*
- *NGUYÊN TẮC VÀNG - LẮNG NGHE CƠ THỂ:** - Nếu thấy ngựcbắt đầu nặng nhẹ, khó chịu - **dừng ngay lập tức**, nghỉ cho đến khi hết hoàn toàn -*
- ***Quan trọng nhất: Bác PHẢI NGHE THEO LỜI BÁC SĨ ĐIỀU TRỊ TRỰC TIẾP CHO BÁC.** Con chỉ giải thích thêm để bác hiểu rõ hơn tại sao lại như vậy,*

### CANNOT — 28× — suggested: `SPELL`
- *Tôi CANNOT chẩn đoán, nhưng phải khuyên đến bệnh viện ngay.*
- ***Lưu ý**: Tôi CANNOT và KHÔNG ĐƯỢC phép chẩn đoán hay thay đổi thuốc, nhưng có thể giải thích tại sao triệu chứng vẫn còn và tại s*
- *The prompt says "Clarify you CANNOT prescribe or diagnose definitively".*

### RESPONSE — 28× — suggested: `SPELL`
- ***RESPONSE STRATEGY**: 1.*
- *Confirm completion: Nếu bác hài lòng, thêm **RESPONSE FORMAT**: - Safety netting (1-2 câu) - Check understanding (1 câu) - Check satisfaction (1 câu) - Không hỏi q*
- *u, nôn ra máu - Sút cân không rõ nguyên nhân - Triệu chứng không cải thiện sau 2-4 tuần **RESPONSE STRATEGY**: - Tóm tắt ngắn gọn (1-2 câu) - An toàn netting (1-2 câu) - Kết thúc ấ*

### ORESOL — 27× — suggested: `SPELL`
- *o bé uống một ít nước dừa nếu bé chịu, nhưng lưu ý nước dừa không thay thế được hoàn toàn ORESOL trong trường hợp mất nước.*
- ***Về ORESOL**: Nếu bé có dấu hiệu mất nước (khô môi, ít nước tiểu, mệt lả), em nên cho bé uống ORESOL theo hướng dẫn trên*
- *ORESOL**: Nếu bé có dấu hiệu mất nước (khô môi, ít nước tiểu, mệt lả), em nên cho bé uống ORESOL theo hướng dẫn trên bao bì.*

### GGT — 27× — suggested: `SPELL`
- ***Xét nghiệm máu**: Kiểm tra men gan (ALT, AST), bilirubin, GGT để đánh giá chức năng gan.*
- ***Xét nghiệm máu**: Kiểm tra men gan (AST, ALT, GGT), bilirubin để đánh giá chức năng gan mật và xem có nhiễm trùng hay tắc mật không.*
- *- **Cận lâm sàng cần thiết**: Xét nghiệm máu (Men gan AST, ALT, GGT, Bilirubin), Siêu âm gan.*

### TMH — 27× — suggested: `SPELL`
- *Chị có thể tra cứu danh sách các bệnh viện có chuyên khoa TMH trên website của Sở Y tế TP.HCM hoặc gọi tổng đài 1080 để hỏi thông tin.*
- *ng có bệnh nền gì cả, cũng không uống thuốc gì thường xuyên mấy viên thuốc nhỏ tai bác sĩ TMH kê thôi ạ.*
- ***Đi khám chuyên khoa TMH ngay**: Ưu tiên để xác định chính xác nguyên nhân và có phác đồ điều trị phù hợp 2.*

### DNA — 27× — suggested: `SPELL`
- *iệm: công thức máu, chức năng gan (AST, ALT, bilirubin), định lượng virus viêm gan B (HBV DNA), và siêu âm gan **Lưu ý an toàn quan trọng**: Nếu anh/chị thấy: - Đau bụng dữ dội - N*
- *Da chúng ta có sắc tố melanin để bảo vệ, nhưng khi tiếp xúc quá nhiều với tia UV từ nắng, DNA trong tế bào da có thể bị hư hại, dẫn đến tế bào phát triển sai và ung thư.*
- ***Tại sao nắng gây ung thư**: Tia UV giống như "tia laser nhỏ" chiếu vào da, làm đứt gãy DNA.*

### DO — 27× — suggested: `SPELL`
- *VỀ VIÊM XOANG DO NẤM:** Bác đừng quá lo lắng.*
- *c:** Theo tôi biết, tập thể dục đều đặn như chạy bộ 5K buổi sáng CÓ THỂ GIÚP GIẢM ĐAU ĐẦU DO CĂNG THẲNG vì: - Giảm stress, tăng endorphin - Cải thiện tuần hoàn máu - Giúp ngủ tốt h*
- *Acid uric cần được kiểm soát lâu dài - Nhưng bác có thể **ăn uống TỰ DO HƠN** so với giai đoạn cấp tính, vẫn phải duy trì hạn chế ở mức độ vừa phải **Tôi giải thích vậy bác có hiểu*

### RUQ — 27× — suggested: `SPELL`
- *- Region: Đau đúng vị trí RUQ (trên rốn bên phải), không lan.*
- ***Tình huống hiện tại**: - Đã thu thập đủ thông tin: Đau RUQ âm ỉ, ăn vào tăng nặng, ~1 tuần, nước tiểu vàng sậm, mệt mỏi, không sốt, không vàng da/mắt, không tiền sử bện*
- ***Phân tích lâm sàng**: - Dấu hiệu đáng chú ý: Đau RUQ + nước tiểu vàng sậm + ăn vào tăng nặng.*

### SJS — 27× — suggested: `SPELL`
- *Allopurinol là một trong những thuốc có thể gây **Stevens-Johnson Syndrome (SJS)** - một phản ứng dị ứng thuốc nặng gây tổn thương da và niêm mạc.*
- *Có nguy hiểm không?** **CÓ.** SJS là tình trạng đe dọa tính mạng nếu không điều trị kịp thời.*
- *Sau khi điều trị SJS xong, có được dùng allopurinol lại không?** **KHÔNG.** Bác sẽ phải kiêng allopurinol vĩnh viễn.*

### AS — 26× — suggested: `SPELL`
- ***Viêm cột sống dính khớp (AS)**: Đây là bệnh viêm mạn tính ảnh hưởng đến cột sống và khớp hông, đặc trưng bởi đau lưng dưới, cứng buổi sán*
- *Để biết chắc chắn em có bị AS hay không, em cần được thăm khám trực tiếp bởi bác sĩ chuyên khoa Cơ xương khớp.*
- ***Câu hỏi**: Chuẩn bị câu hỏi muốn hỏi bác sĩ (ví dụ: "Em có bị AS không?", "Có cần kiêng gì không?").*

### NCS — 26× — suggested: `SPELL`
- *n kinh, bác sĩ có thể chỉ định làm **điện cơ (EMG)** và **đo tốc độ dẫn truyền thần kinh (NCS)**.*
- ***Điện cơ (EMG) và điện thần kinh (NCS)**: Để đánh giá xem dây thần kinh có bị tổn thương hay không và mức độ tổn thương.*
- *, bác sĩ có thể sẽ chỉ định làm **điện cơ đồ (EMG)** và **đo tốc độ dẫn truyền thần kinh (NCS)** để kiểm tra xem dây thần kinh giữa của mình có bị chèn ép không và mức độ chèn ép n*

### QUEN — 26× — suggested: `SPELL`
- ***NHỮNG THÓI QUEN TỐT EM NÊN LÀM:** 1.*
- *THÓI QUEN SINH HOẠT**: - [ ] Ngủ: tư thế nào?*
- *- **THÓI QUEN SINH HOẠT**: Không nằm ngay sau ăn, mặc quần áo rộng, giữ cân nặng khỏe mạnh.*

### CONTINUE — 25× — suggested: `SPELL`
- *[[CONTINUE]]*

### ASD — 25× — suggested: `SPELL`
- ***Về vấn đề tim mạch của em:** Thất tâm nhĩ (ASD) nếu vẫn còn lỗ thủng khi em lớn lên, có thể gây ra các vấn đề nghiêm trọng như: - Tăng áp lực trong mạch máu*
- *Em nên: - Khám tim mạch toàn diện - Siêu âm tim (echocardiogram) để đánh giá ASD và chức năng tim - Có thể cần điện tâm đồ, Holter monitor **Lưu ý an toàn:** Nếu em cảm thấy khó th*
- *Em chỉ nhớ là mẹ em từng kể là em bị "thất tâm nhĩ" (ASD) - một lỗ thủng ở tim khi mới sinh.*

### PSG — 25× — suggested: `SPELL`
- *tôi giải thích ngắn gọn về các xét nghiệm thường làm: **Test giấc ngủ (Polysomnography - PSG)** là xét nghiệm chính: - **Tại bệnh viện**: Em sẽ ngủ lại qua đêm tại bệnh viện, các t*
- ***Đo đa ký giấc ngủ (Polysomnography - PSG)**: Đây là xét nghiệm chính.*
- *rong lúc ngủ và thức để phát hiện các bất thường - **Đo đa ký giấc ngủ (Polysomnography - PSG)**: Em sẽ ngủ lại một đêm tại bệnh viện để theo dõi toàn bộ giấc ngủ, nhịp tim, hô hấp*

### HSG — 25× — suggested: `SPELL`
- ***Có thể cần thêm (tùy bác sĩ chỉ định):** - Hysterosalpingography (HSG): Chụp buồng tử cung vòi trứng xem có tắc không - Xét nghiệm di truyền nếu cần **Về chi phí:** Tôi thành thậ*
- *Chẩn đoán hình ảnh chuyên sâu**: MRI tử cung buồng trứng, siêu âm bơm nước buồng tử cung (HSG) để kiểm tra vòi trứng - **Xét nghiệm miễn dịch**: Kiểm tra các kháng thể ảnh hưởng đế*
- *Đánh giá ống dẫn trứng:** Nếu cần, bác sĩ có thể chỉ định chụp X-quang tử cung vòi trứng (HSG) để xem ống dẫn trứng có thông suốt không.*

### BBQ — 24× — suggested: `SPELL`
- *Tôi cũng chán ăn, không còn hứng thú với những món mình từng thích, như là nướng BBQ hay tôm nướng.*
- ***Về tình trạng hiện tại**: Những gì anh/chị mô tả - mất ngủ, mất niềm vui trong nấu BBQ, cảm giác vô nghĩa, mất phương hướng - là những triệu chứng của **trầm cảm nặng**.*
- ***Về việc nấu BBQ**: Thay vì từ bỏ, hãy thử: - Nấu cho chính mình với số lượng nhỏ hơn - Chia sẻ thành phẩm với hàng xóm hoặc đ*

### MAI — 24× — suggested: `SPELL`
- ***Bác CẦN ĐI KHÁM NGAY HÔM NAY hoặc NGÀY MAI** tại bệnh viện có chuyên khoa Tim mạch.*
- *BÁC NÊN ĐI KHÁM NGAY HÔM NAY HOẶC NGÀY MAI.** Tại sao ạ?*
- ***TÓM TẮT KẾ HOẠCH CỦA CHỊ MAI:** ✅ **Tự chăm sóc tại nhà 1-2 tuần**: Nghỉ ngơi, chỉnh tư thế làm việc, tập stretches nhẹ nhàng như đã trao*

### MCI — 24× — suggested: `SPELL`
- *lão hóa tự nhiên, nhưng cũng có thể là dấu hiệu của suy giảm trí nhớ lành tính tuổi già (MCI) - một tình trạng có nguy cơ tiến triển thành bệnh Alzheimer hoặc các bệnh lý khác.*
- ***Suy giảm nhận thức nhẹ (MCI)**: Đây là giai đoạn giữa bình thường và sa sút trí tuệ, có thể cải thiện nếu phát hiện sớm.*
- *i:** Tình trạng của bác có thể là **"Suy giảm nhận thức nhẹ" (Mild Cognitive Impairment - MCI)** - một dạng suy giảm trí nhớ ở người cao tuổi.*

### HTA — 24× — suggested: `SPELL`
- *Bác sĩ sẽ: - Làm các test trí nhớ chuyên sâu - Kiểm tra lại các bệnh nền (HTA, tiểu đường) có đang được kiểm soát tốt không - Có thể cần xét nghiệm máu, chụp não nếu cần **Lưu ý qu*
- *Ở bác, với tiền sử HTA, tiểu đường, cần kiểm tra kỹ để loại trừ nguyên nhân thứ cấp.*
- *Prospan: relatively an toàn, chiết xuất thảo dược, không ảnh hưởng nhiều đến HTA/ĐTĐ 2.*

### CAD — 24× — suggested: `SPELL`
- **Phân tích**: - Đây là hình ảnh điển hình của **bệnh mạch vành (Coronary Artery Disease - CAD)** hoặc **rối loạn nhịp tim**.*
- *Bác làm kỹ sư cơ khí, trước đây bác rất minh mẫn, làm việc với CAD, CNC cả ngày mà không sao.*
- *Tôi cũng không rõ nguyên nhân do đâu, có thể do tôi thường xuyên phải dùng phần mềm CAD trên máy tính hay không.*

### SVT — 24× — suggested: `SPELL`
- ***Rối loạn nhịp tim lành tính (SVT, PAC)**: Có thể, nhưng thường kèm theo triệu chứng rõ rệt hơn (choáng váng).*
- *osis**: Thiếu tập luyện thể chất (deconditioning), Hen suyễn gắng sức, Rối loạn nhịp tim (SVT, PAC), Bệnh lý van tim (hẹp van hai lá, hở van...), Bệnh lý toàn thân (Thiếu máu, Suy *
- *tự hết), đây có thể là một dạng rối loạn nhịp tim như cơn nhịp nhanh kịch phát trên thất (SVT) hoặc cũng có thể do cơ thể phản ứng với căng thẳng vô thức.*

### CO — 23× — suggested: `SPELL`
- *hChCh có ChChCh Ch ChCCCC có có có Ch O hỏi có Ch Ch, Ch Ch chO0 ChChCh b +oCC ChCh Ch + +CO là là + + b CC +C M ��C/c b b +�CC b Ch có���� ��C�� +��CCCC� ch����CCCCCCC������������*
- ***Trong tuần này**: Đi khám bác sĩ để được làm xét nghiệm khí CO và đánh giá toàn diện 3.*
- ***Về xét nghiệm**: - **Xét nghiệm khí CO trong máu**: Đúng là có xét nghiệm này, nó kiểm tra nồng độ carbon monoxide hemoglobin trong máu, giúp xác đị*

### UBND — 23× — suggested: `EXPAND` → `uỷ ban nhân dân`
- *àng sớm càng tốt - Ở Bình Dương, Mai có thể liên hệ Bệnh viện Đa khoa tỉnh, Sở Y tế, hoặc UBND địa phương để được hỗ trợ về chi phí **Điều quan trọng nhất lúc này**: Thay vì lo lắn*
- *hệ **Sở Y tế tỉnh Bình Dương** để hỏi về chính sách hỗ trợ bệnh nhân khó khăn - Tìm đến **UBND phường/xã** để được tư vấn về các chương trình hỗ trợ y tế địa phương - Hỏi tại **Trạ*
- *cho con trai hoặc đến Hội Chữ thập đỏ Hà Nội (số điện thoại có thể tìm trên mạng hoặc hỏi UBND phường) 2.*

### HVAC — 23× — suggested: `SPELL`
- *Bác cũng có tiền sử làm HVAC leo trèo sửa chữa, và hiện tại vẫn làm vườn, mộc, và mang vác nặng khi tình nguyện.*
- *Tôi trước đây làm kỹ thuật viên HVAC, hay leo trèo và sửa chữa máy lạnh, nhưng hiện tại tôi đã nghỉ việc rồi.*
- *- Làm phòng máy lạnh → có thể bụi mạt, nấm mốc trong hệ thống HVAC.*

### CEO — 23× — suggested: `SPELL`
- *Tôi là CEO của một công ty, thường xuyên phải làm việc với máy tính và điện thoại nhiều giờ liền, thỉnh thoảng phải khuâ*
- *Vì tính chất công việc của em là một người điều hành startup (CEO), nên em phải làm việc nhiều với máy tính, gõ phím và sử dụng chuột rất nhiều.*
- *Tôi cũng muốn hỏi thêm: **Về công việc của tôi**, tôi là CEO của một công ty, thường phải họp nhiều và ngồi làm việc với máy tính cả ngày.*

### S1 — 23× — suggested: `SPELL`
- *Bác sĩ chẩn đoán là thoát vị đĩa đệm L4-L5, L5-S1.*
- ***Trước hết, về câu hỏi "bệnh này có nguy hiểm không":** Thoát vị đĩa đệm L4-L5, L5-S1 là tình trạng khá phổ biến ở người trẻ.*
- *:** - Đau âm ỉ, tê buốt, kiến bò ở mông phải, lan mặt sau đùi → **ngón út chân phải** (rễ S1).*

### B3 — 23× — suggested: `SPELL`
- *NIACINAMIDE (Vitamin B3)** - **Cơ chế**: ức chế melanin di chuyển lên da, chống viêm, cải thiện hàng rào da - **Hiệu quả**: Giúp mờ đ*
- *Kem Niacinamide (hoặc B3)**: - **Tác dụng**: Làm mờ đốm nâu, dưỡng ẩm, kiềm dầu (nhưng da Anh/Chị khô thì vẫn ok) - **Cách dùng**: Buổ*
- *� B3 Ch ăn ăn chọn chọn.*

### ID — 22× — suggested: `SPELL`
- *- **Thẻ bảo hiểm/ID và tiền** (nếu có).*
- ***Tìm kiếm online**: Em có thể dùng Google search "Rheumatologist near Shelley, ID" hoặc dùng các trang web như Zocdoc, Healthgrades để xem đánh giá và đặt lịch khám online.*
- *vận hành nhà máy, triệu chứng này làm em khó tập trung lắm, nhất là khi phải đọc bản vẽ P&ID hay kiểm tra hệ thống ống dẫn.*

### OR — 22× — suggested: `SPELL`
- *knowledgment] [1-2 sentences of relevant info/education if needed] [1-2 focused questions OR action recommendation]".*
- *The prompt says "[1-2 focused questions OR action recommendation]".*
- *ey just said] [1-2 sentences of relevant info/education if needed] [1-2 focused questions OR action recommendation]" Tôi nên làm theo quy tắc này.*

### CPA — 22× — suggested: `SPELL`
- *Tôi đang chuẩn bị thi CPA nên không muốn ảnh hưởng đến việc học.*
- *Gần đây tôi có tăng giờ làm thêm để chuẩn bị cho kỳ thi CPA nên có vẻ tôi ngồi lâu hơn bình thường.*
- ***Các cách giảm triệu chứng tại nhà cho chị (trong khi chuẩn bị thi CPA):** 1.*

### TRUNG — 22× — suggested: `SPELL`
- *Tuy nhiên, tôi **PHẢI TRUNG THỰC VÀ BẢO VỆ AN TOÀN TÍNH MẠNG** của Anh/Chị.*
- *- **Tương lai phụ thuộc vào: nguyên nhân + tốc độ điều trị + đáp ứng của cháu** **HÃY TẬP TRUNG VÀO HIỆN TẠI**: Đưa cháu đến bệnh viện ngay, cung cấp thông tin đầy đủ cho bác sĩ.*
- *ộng rãi, dễ tháo lắp - Mang theo BHYT, CMND/CCCD **Lưu ý quan trọng:** - Khi khám, hãy kể TRUNG THỰC tất cả triệu chứng, không nên nói giảm nói tránh - Đừng ngại hỏi bác sĩ về chi *

### OK — 22× — suggested: `SPELL`
- *ton thoáng - Tránh các chất kích thích như rượu, cà phê nhiều **Về đi hiking**: Hoàn toàn OK!*
- ***Kiểm tra quy tắc**: - Không chẩn đoán: OK.*
- *- Không kê đơn: OK.*

### SUY — 22× — suggested: `SPELL`
- *c và KHÔNG khó thở đột ngột → KHÔNG phù hợp với tràn khí màng phổi cấp tính - Triệu chứng SUY TIM: ho khan, khó thở khi vận động, có thể không đau ngực → CÓ THỂ - Triệu chứng VIÊM *
- *Nhưng **KHÔNG NÊN TỰ SUY ĐOÁN**.*
- ***VỀ UỐNG NƯỚC KHI BỊ SUY TIM THAI:** **1.*

### CRPS — 22× — suggested: `SPELL`
- ***Hội chứng Sudeck** (hay còn gọi là Rối loạn đau phức hợp vùng - CRPS) là một tình trạng đau mạn tính thường xảy ra sau chấn thương, dù là chấn thương nhẹ, khiến hệ thần kinh và m*
- ***Về bệnh "Sudeck" (hay còn gọi là CRPS - Hội chứng đau vùng phức hợp)**: Đây là một tình trạng đau mãn tính thường xuất hiện sau khi bị chấn thương,*
- ***Về "hội chứng Sudeck" (CRPS):** Đây là một hội chứng đau mạn tính, thường xảy ra sau chấn thương, với đặc điểm: - Đau dữ dội, không tương*

### LED — 21× — suggested: `SPELL`
- *Em nên dùng kem chống nắng có SPF 30-50 mỗi ngày, kể cả trong nhà vì đèn LED và màn hình máy tính.*
- ***Tiếp xúc ánh sáng xanh**: Ánh sáng từ màn hình và đèn LED làm tăng tốc độ lão hóa da.*
- *sóc da cơ bản**: Sử dụng kem dưỡng ẩm đơn giản và kem chống nắng (kể cả trong nhà vì đèn LED).*

### TW — 21× — suggested: `SPELL`
- *Hỏi trực tiếp bác sĩ tại BV Phụ sản TW về các phác đồ và chi phí ước tính 2.*
- *Anh nên tiếp tục trao đổi với bác sĩ chuyên khoa tại BV Phụ sản TW để có plan điều trị phù hợp nhất cho hai vợ chồng.*
- *nh xác ✅ **Bước 2:** Anh/chị đi khám tổng quát sức khỏe ✅ **Bước 3:** Quay lại BV Phụ sản TW để bác sĩ chuyên khoa tư vấn cụ thể **Và quan trọng nhất:** Sau khi có kết quả khám, bá*

### TRT — 21× — suggested: `SPELL`
- *ng, bác sĩ có thể cân nhắc liệu pháp hormone thay thế (Testosterone Replacement Therapy - TRT).*
- *Liệu pháp thay thế testosterone (TRT):** - Đây là thuốc hormone do bác sĩ chỉ định sau khi có chỉ định y tế - Có nhiều dạng: gel bôi, tiêm, miếng*
- ** **Liệu pháp hormone (TRT - Testosterone Replacement Therapy):** * Đây là phương pháp dùng thuốc bổ sung testosterone **chỉ được chỉ đị*

### KINH — 20× — suggested: `SPELL`
- *KHI ĐI KHÁM THẦN KINH, BÁC SĨ SẼ LÀM GÌ?** - **Hỏi bệnh chi tiết**: Hỏi bác về tình trạng hay quên, thời gian, mức độ - **Làm test*
- *bác đã mãn kinh, nếu có triệu chứng như đau bụng, đau lưng và đặc biệt là RA MÁU SAU MÃN KINH, đây là những dấu hiệu cần được đánh giá kỹ lưỡng.*
- *mạc tử cung**: do thay đổi nội tiết sau mãn kinh Quan trọng là triệu chứng RA MÁU SAU MÃN KINH cần được kiểm tra để loại trừ nguyên nhân nghiêm trọng, nhưng đa số trường hợp không *

### B5 — 20× — suggested: `SPELL`
- *- **Vitamin B5 (Pantothenic acid)**: Giúp da đầu khỏe mạnh.*
- ***Kem bôi đặc hiệu**: Vaseline không hiệu quả bằng các loại kem chứa Panthenol (vitamin B5) hoặc Hydrocortisone 0.5% (thấp nhất) để làm lành vết nứt.*
- *ồi da**: Ceramide, Glycerin, Hyaluronic acid - **Thành phần làm dịu**: Panthenol (vitamin B5), Niacinamide - **Đặc tính**: Dạng kem (cream) chứ không lotion (kem đặc hơn, dưỡng ẩm *

### DM2 — 20× — suggested: `SPELL`
- *- **PMH**: Cao huyết áp (HTN), Tiểu đường type 2 (DM2) - 2 yếu tố nguy cơ quan trọng.*
- ***Yếu tố nguy cơ**: Tuổi 67, HTN 3 năm, DM2 type 2 (dù đường huyết ổn định).*
- *- **PMH**: HTN (3 năm), DM2 type 2.*

### CCP — 20× — suggested: `SPELL`
- *ngờ viêm khớp dạng thấp (do Anh/Chị có nhắc đến), họ sẽ chỉ định xét nghiệm máu (RF, anti-CCP) để loại trừ.*
- *c khớp - **Xét nghiệm máu**: Tìm yếu tố viêm (CRP, ESR), yếu tố thấp (RF), kháng thể anti-CCP (nếu nghi ngờ viêm khớp dạng thấp) - **Chụp X-quang**: Để xem tình trạng khớp, có bị ă*
- *- **Xét nghiệm cần làm**: Bác sĩ sẽ chỉ định xét nghiệm máu (RF, Anti-CCP, CRP, ESR) để đánh giá viêm và X-quang khớp để xem mức độ tổn thương.*

### BHXH — 20× — suggested: `EXPAND` → `bảo hiểm xã hội`
- *để hỏi về chi phí phẫu thuật trĩ - **Gọi tổng đài BHYT** (số 1900.9068) hoặc đến cơ quan BHXH nơi anh đóng BHYT để được tư vấn về mức độ chi trả - **Hỏi trực tiếp bác sĩ** sau khi *
- *- **Hoặc tổng đài BHXH Việt Nam** (số 1900.9068) để được giải đáp về quyền lợi bảo hiểm.*
- *Về chế độ ốm đau của Bảo hiểm xã hội (BHXH):** Nếu bác có sổ BHXH và đang đóng đều đặn, khi bị ốm đau như thế này, bác sẽ được hưởng chế độ ốm đau.*

### DOMS — 20× — suggested: `SPELL`
- *sẻ, cơn đau mỏi này có vẻ như là tình trạng **đau cơ do vận động quá mức** (thường gọi là DOMS), rất phổ biến khi cơ thể phải làm việc nặng đột ngột hoặc lặp lại động tác nhiều lần*
- *Anh nghĩ đây có thể là tình trạng đau cơ do vận động mạnh (DOMS) hoặc cơ bị kéo giãn nhẹ khi chơi.*
- *Em à, trước giờ em có biết về DOMS (Delayed Onset Muscle Soreness) không?*

### BP — 19× — suggested: `SPELL`
- *- Main concern: painless hematuria for 2 weeks, pink urine - Medications: Amlodipine 5mg (BP med), Glucosamine 1500mg (supplement) - Functional impact: minimal - no fatigue, normal*
- **xpectations: Muốn biết có sao không, có cần thuốc không **Clinical Logic**: - 53yo male, BP 130/80 (pre-hypertension) - QRS widening on ECG - Exertional dyspnea/fatigue for 1 year*
- *iomyopathy - Need: echocardiogram, stress test, possibly Holter - Risk factor: borderline BP **Question Count**: Không cần hỏi thêm.*

### UNG — 19× — suggested: `SPELL`
- *Nhưng **u bã đậu KHÔNG PHẢI UNG THƯ** con nhé!*
- *--- ### **BÀI TẬP 1: ĐUNG ĐƯA VAI (Pendulum Swings)** **Mục đích**: Kéo giãn nhẹ nhàng, giảm căng cơ **Cách tập**: 1.*
- ***Về các nguyên nhân KHÔNG PHẢI UNG THƯ:** - **Polyp tử cung**: là khối u lành tính, có thể gây ra máu - **Viêm nhiễm phụ khoa**: có thể gây chảy*

### CSC — 19× — suggested: `SPELL`
- *đáp thắc mắc của Anh: **Về nguy hiểm và điều trị:** Trường hợp "lạc nội mạc hoàng điểm" (CSC) nếu đúng là bệnh này, thường **không phải là bệnh nguy hiểm đến mức mất thị lực hoàn t*
- ***Tình huống**: - Không dùng corticosteroid → loại trừ CSC do thuốc.*
- *ìn đường thẳng bị cong nhẹ - là dấu hiệu điển hình của hắc võng mạc trung tâm thanh dịch (CSC).*

### FLAG — 19× — suggested: `SPELL`
- *ả năng cao: Viêm khớp nhiễm trùng (septic arthritis) hoặc viêm khớp cấp tính khác - **RED FLAG**: Đau dữ dội, sưng đỏ nóng, không có chấn thương - cần loại trừ nhiễm trùng **Safety*
- *Nuốt nghẹn với tất cả thức ăn (đặc biệt cơm) - RED FLAG 2.*
- *Sút 3kg trong 2 tháng - RED FLAG 3.*

### MRA — 19× — suggested: `SPELL`
- *thương khác, và siêu âm động mạch cảnh (để xem có hẹp hay không) hoặc chụp mạch máu não (MRA/DSA).*
- *Chụp MRI mạch máu (MRA)**: - Dùng máy MRI (từ trường) để chụp mạch máu.*
- *ảnh chi tiết, nhanh chóng, nhưng có dùng thuốc cản quang và tia X - **Chụp MRI mạch máu (MRA)**: Không dùng tia X, cho hình ảnh tốt, nhưng mất thời gian hơn và có thể không phù hợp*

### EBV — 19× — suggested: `SPELL`
- *họng**: Bệnh này thực ra rất hiếm ở người trẻ dưới 30 tuổi, và thường liên quan đến virus EBV.*
- *Các bệnh như lao (TB), hoặc các virus như EBV, CMV có thể gây mệt mỏi và sốt nhẹ kéo dài.*
- *ăm khám trực tiếp và làm các xét nghiệm chuyên sâu hơn như: xét nghiệm virus chuyên biệt (EBV, CMV, viêm gan tự miễn), siêu âm gan, hoặc có thể sinh thiết gan nếu cần.*

### B7 — 18× — suggested: `SPELL`
- *c khỏe da đầu, nhưng bác sĩ Meddies khuyên em nên tập trung vào 2 nhóm chính: - **Vitamin B7 (Biotin)**: Tốt cho tóc và da đầu.*
- *u hụt một số vi chất dinh dưỡng quan trọng cho sự phát triển của móng như Biotin (vitamin B7) hay Kẽm.*
- *Khi cơ thể thiếu hụt protein, vitamin (đặc biệt biotin - vitamin B7), khoáng chất như kẽm, canxi, móng sẽ yếu đi và thay đổi màu sắc.*

### TAY — 18× — suggested: `LOWERCASE` → `tay`
- *ĐAU NGỰC KÉO DÀI TRÊN 15 PHÚT**, **KHÓ THỞ NẶNG**, **MẤT Ý THỨC**, hoặc **ĐAU LAN RA CÁNH TAY/CẰM**, hãy **GỌI 115 NGAY** hoặc đến bệnh viện gần nhất.*
- *BÀI TẬP CHO TAY (làm 3-4 lần/ngày, mỗi lần 5 phút):** 1.*
- *dẫn chi tiết các bài tập anh/chị có thể làm tại nhà trong thời gian bó bột: **BÀI TẬP CHO TAY VÀ THÂN TRÊN (2-3 lần/ngày, mỗi lần 10-15 phút):** **1.*

### NEVER — 18× — suggested: `SPELL`
- *Actually, the instruction says "NEVER ask questions about information already provided." They already told me about the lump characteristics.*
- *This might be a test to see if I'll repeat myself (which is against the rules - "NEVER ask questions about information already provided").*
- *losed questions - Câu hỏi của tôi là closed questions, nhưng hợp lý trong hoàn cảnh này - NEVER ask questions about information already provided - Tôi không hỏi lại thông tin đã có*

### NAM — 18× — suggested: `LOWERCASE` → `nam`
- ***CÁCH CHĂM SÓC TẠI NHÀ CHO CHÁU NAM:** **1.*
- ***AN TOÀN CHO CHÁU NAM:** Nếu cháu thấy: - Da sưng đỏ, có mủ - Ngứa rất nhiều, không ngủ được - Hoặc sau 1-2 tuần không đỡ **Bác/Chị*
- *- Có thể gây khô, bong nhẹ ban đầu - Không dùng khi đang mang thai **VỀ SẢN PHẨM TẠI VIỆT NAM:** - **Dễ tìm ở hiệu thuốc/siêu thị**: - The Ordinary (Niacinamide 10%, Vitamin C 15%)*

### PVD — 18× — suggested: `SPELL`
- *Đây có thể là **bong dịch kính sau (PVD)** hoặc **bong võng mạc**.*
- *This is consistent with Posterior Vitreous Detachment (PVD), a common age-related change.*
- *Likely Posterior Vitreous Detachment (PVD).*

### PDA — 18× — suggested: `SPELL`
- *Patient đã cung cấp đủ thông tin về tiền sử không điều trị PDA và triệu chứng.*
- *mạnh - Không phù, không khó thở khi nằm hay ho về đêm **Về tình trạng còn ống động mạch (PDA):** Đây là một lỗ thông giữa động mạch phổi và động mạch chủ.*
- ***Suy tim do PDA** - tim phải làm việc quá sức 3.*

### TX — 18× — suggested: `SPELL`
- *Mẹ em có thể tìm kiếm trên Google: "Pediatrician near me Dallas TX" hoặc "Pediatric gynecologist Dallas TX" để xem đánh giá và chọn nơi phù hợp.*
- *ìm kiếm trên Google: "Pediatrician near me Dallas TX" hoặc "Pediatric gynecologist Dallas TX" để xem đánh giá và chọn nơi phù hợp.*
- *brook** (khoảng 15-20 phút từ Spring) - Có dịch vụ phiên dịch tiếng Việt - Địa chỉ: 18222 TX-249, Houston, TX 77070 2.*

### REM — 18× — suggested: `SPELL`
- *ọng là cần đi khám để loại trừ các nguyên nhân khác (động kinh ban đêm, rối loạn giấc ngủ REM...).*
- *- Mơ thấy té từ trên cao xuống là dấu hiệu của **Rối loạn giấc ngủ REM** hoặc các cơn **ngưng thở khi ngủ** (hội chứng ngưng thở tắc nghẽn - OSA).*
- *nghe về các rối loạn giấc ngủ như Narcolepsy (chứng ngủ rũ) hay Rối loạn hành vi giấc ngủ REM chưa em?** Dựa trên những gì em chia sẻ, tôi có thể cho em biết: - Đây không phải là t*

### HELLP — 18× — suggested: `SPELL`
- *Đây có thể là dấu hiệu của **tiền sản giật** hoặc **hội chứng HELLP** - các biến chứng thai kỳ nghiêm trọng cần điều trị kịp thời.*
- *Đây có thể là dấu hiệu của **tiền sản giật** hoặc **hội chứng HELLP**, những biến chứng thai kỳ có thể đe dọa tính mạng cả mẹ và bé.*
- *Bác nghe bác sĩ chẩn đoán hội chứng HELLP, đây là một tình trạng y tế nghiêm trọng cần phải theo dõi sát sao.*

### MASSAGE — 17× — suggested: `SPELL`
- ***HƯỚNG DẪN MASSAGE MẶT GIẢM NẾP NHĂN:** **Chuẩn bị:** - Rửa sạch tay - Thoa một ít dầu ô liu/dầu dừa hoặc kem dưỡng đã làm - Mas*
- *oay cằm sang vai trái (giữ 5-10 giây) - Xoay sang vai phải - Lặp lại 3-5 lần mỗi bên **VỀ MASSAGE TẠI NHÀ:** Có thể massage nhẹ nhàng vùng cổ và vai gáy bằng cách: - Dùng ngón tay *
- *MASSAGE VÀ VẬT LÝ TRỊ LIỆU (Giảm đau nhanh)** - **Cách làm**: Đến các phòng khám vật lý trị liệu hoặc massage y khoa*

### VAI — 17× — suggested: `SPELL`
- *BÀI TẬP CỔ VÀ VAI:** - Mỗi giờ, dành 2-3 phút: - Xoay c cổ nhẹ nhàng trái-phải, lên-xuống - Gập c cổ về phía trước, sau, nghiên*
- ***CÁC BÀI TẬP GIÃN CƠ VAI NHẸ NHÀNG** (em tập từ từ, không gắng sức): 1.*
- *--- ### **BÀI TẬP 1: ĐUNG ĐƯA VAI (Pendulum Swings)** **Mục đích**: Kéo giãn nhẹ nhàng, giảm căng cơ **Cách tập**: 1.*

### Q1 — 17× — suggested: `SPELL`
- **Let's combine and prioritize.* * Q1: "Anh/chị có thể cho biết tên loại thuốc ho và xịt mũi bé đang dùng không ạ?" (Safety check).*
- *chịu." * Transition: "Để tôi có thể tư vấn chính xác hơn, tôi cần hỏi thêm:" * Questions: Q1 (Meds), Q2 (Swelling severity).*
- *I will assume this is the correct interpretation.* *Final check on questions:* Q1: "Anh/chị có thể cho biết tên loại thuốc ho và xịt mũi bé đang dùng không ạ?" -> Clear, necessary.*

### GP — 17× — suggested: `SPELL`
- ***Thời gian**: Khám GP thường nhanh hơn, có thể lấy hẹn trong tuần.*
- ***Lời khuyên thực tế:** - Nếu triệu chứng không nặng (như em mô tả), khám GP trước là hợp lý và tiết kiệm thời gian - Mang theo nhật ký triệu chứng để bác sĩ gia đình đánh giá chín*
- *Đi khám bác sĩ gia đình (GP):** - Ưu điểm: Đánh giá tổng quát, xét nghiệm máu (đường huyết, công thức máu, mỡ máu) để loại trừ các nguyên*

### MRCP — 17× — suggested: `SPELL`
- *Nếu siêu âm bình thường mà triệu chứng vẫn rõ, bác sĩ có thể chỉ định thêm xét nghiệm MRCP (chụp MRI đường mật) hoặc nội soi để kiểm tra kỹ hơn.*
- ***Chụp MRI ống mật tụy (MRCP)**: Không tia X, nhìn rõ hệ thống ống dẫn dịch tụy và mật.*
- ***Chụp MRCP** (chụp cộng hưởng từ đường mật) để đánh giá kỹ kích thước và tình trạng nang, từ đó bác sĩ mới quyết định ph*

### BCG — 17× — suggested: `SPELL`
- *Và em có nhớ là em đã tiêm phòng lao (vắc-xin BCG) khi còn nhỏ không ạ?*
- *Em đã tiêm phòng lao (vắc-xin BCG) chưa?*
- *Và bé đã tiêm chủng đầy đủ các mũi cơ bản, đặc biệt là mũi lao (BCG) chưa ạ?*

### AV — 17× — suggested: `SPELL`
- *N là hình ảnh điển hình của **bệnh nút sino (Sick Sinus Syndrome)** hoặc **block nhĩ-thứ (AV Block)**.*
- *Tôi là thợ điện AV, hay phải leo trèo và làm việc với các thiết bị phức tạp, nhưng vẫn quen rồi.*
- *Tôi nghe nói có cái gọi là "Kênh nhĩ thất" (AV Canal) là gì, có liên quan không?*

### PTH — 17× — suggested: `SPELL`
- *ghiệm máu để kiểm tra: - Nồng độ canxi và phospho trong máu - Mức hormone tuyến cận giáp (PTH) - Chức năng thận - Nồng độ vitamin D Ngoài ra, bác sĩ có thể yêu cầu siêu âm cổ để xá*
- *Về mặt y tế:** - Bác sĩ sẽ yêu cầu các xét nghiệm máu (canxi, phospho, PTH, chức năng thận...), điện tâm đồ, siêu âm hoặc scan - Tiếp tục uống thuốc theo đơn nếu có, đặc biệt là ca*
- *a?** Nếu chưa, tôi xin giải thích ngắn gọn: U tuyến cận giáp có thể làm tăng tiết hormone PTH, dẫn đến mất cân bằng canxi trong máu.*

### VI — 16× — suggested: `SPELL`
- *VIẾT THƯ (dễ nhất nếu cháu ngại nói trực tiếp):** - Viết một mẩu giấy ngắn: "Bố/mẹ ơi, con có mấy triệu chứng đa*
- ***ANH/CHỊ CẦN ĐẾN BỆNH VIỆN KHẨN CẤP NGAY LẬP TỨC (gọi 115 hoặc đến khoa Cấp cứu gần nhất).*
- *VỀ VIỆC MUA THUỐC:** Tôi **KHÔNG THỂ** tư vấn cho anh mua thuốc cụ thể hay liều lượng nào.*

### EGD — 16× — suggested: `SPELL`
- *ệu chứng như bác đã kể với Tôi - **Thăm khám lâm sàng** - **Nội soi thực quản - dạ dày** (EGD) là xét nghiệm chính để quan sát trực tiếp bên trong - Có thể làm thêm **chụp cản quan*
- ***Nội soi dạ dày thực quản (EGD):** Đây là xét nghiệm quan trọng nhất để bác sĩ có thể quan sát trực tiếp bên trong thực quản của chị bằng mộ*
- ***Nội soi dạ dày (EGD)**: Để quan sát trực tiếp niêm mạc dạ dày, tá tràng và tìm kiếm ổ loét, viêm nhiễm hoặc nguồn chảy máu.*

### SLS — 15× — suggested: `SPELL`
- *- Tránh các thành phần như: Sodium Lauryl Sulfate (SLS) nếu da nhạy cảm.*
- ***Về dầu gội, Bác nên tìm các loại có ghi:** - **Thành phần nên tránh**: Sulfate (SLS/SLES), Paraben, Silicon, Fragrance/Parfum (hương liệu), và cồn.*
- *g liệu (fragrance), chất tạo màu, hoặc các chất tẩy rửa mạnh (như sodium lauryl sulfate - SLS).*

### INTERNAL — 15× — suggested: `SPELL`
- ***INTERNAL NOTE**: Tôi đã thu thập được: - Triệu chứng: bí tiểu, rặn mới đi được, tiểu đêm 3-4 lần - Thời gian: gần 1 nă*
- *(INTERNAL REASONING: The patient has asked me to explain more about osteoarthritis.*
- *(INTERNAL REASONING: The patient has not responded to my last message.*

### THAM — 15× — suggested: `SPELL`
- ***Một số hoạt động nhẹ nhàng con có thể THAM KHẢO (nhưng phải được bác sĩ đồng ý):** 1.*
- ***THÔNG TIN CHUNG EM CÓ THỂ THAM KHẢO:** Một số dưỡng chất có thể hỗ trợ sức khỏe tinh thần khi thiếu hụt: - **Vitamin B complex**: Hỗ trợ hệ*
- *Con xin chia sẻ thông tin nhưng **Bác PHẢI THAM VẤN BÁC SĨ TRƯỚC KHI DÙNG BẤT KỲ THUỐC NÀO** nhé: **VỀ THUỐC GIẢM TRIỆU CHỨNG:** Có 2 nhóm thuốc chính thường*

### DI — 15× — suggested: `SPELL`
- *Ở YÊN MỘT CHỖ, ĐỪNG DI CHUYỂN.** Đừng lo lắng về việc chuẩn bị gì hay mở cửa.*
- *ác nặng, leo cầu thang nhiều) - **Quan trọng**: Phải có chẩn đoán chính xác trước đã **VỀ DI TRUYỀN:** - Bệnh tim có yếu tố di truyền, nhưng không phải 100% - **Con cái bác có nguy*
- *Có cần xét nghiệm lại chức năng gan thận không?" **NHÓM 3: VỀ DIỄN BIẾN & THEO DÕI** 7.*

### P2 — 15× — suggested: `SPELL`
- *Cách bảo vệ da khi làm việc hàn:** **Khẩu trang:** - Dùng **khẩu trang N95 hoặc P2** (chứi bụi mịn, khói hàn) - Thay mới khi ướt hoặc bẩn - Đeo kín, che cả mũi và miệng **Trang phụ*
- ***Cách phòng tránh khi làm xây dựng:** - **Đeo khẩu trang đúng cách**: Loại N95 hoặc P2, thay mới khi ướt/bẩn.*
- ***Tại nhà để giảm triệu chứng ngay**: * **Đeo khẩu trang loại tốt (N95 hoặc P2)** khi làm việc, đặc biệt lúc dọn kho.*

### PE — 15× — suggested: `SPELL`
- *- Cần loại trừ huyết khối tĩnh mạch sâu (DVT), thuyên tắc phổi (PE), nhiễm trùng tế bào, loét.*
- *Các loại thuốc điều trị PE cần có chỉ định và theo dõi của bác sĩ chuyên khoa, không nên tự ý dùng.*
- *Điều này có thể giúp cải thiện cả triệu chứng PE và cảm giác mệt mỏi.*

### CLB — 15× — suggested: `SPELL`
- ***Tham gia CLB kịch linh hoạt**: Chọn vai ít thoại hoặc làm đạo diễn để giữ đam mê mà không làm hại giọng.*
- *Em sẽ cân nhắc tham gia CLB kịch với vai trò đạo diễn hoặc biên kịch trong thời gian chờ đợi để không phải bỏ lỡ đam mê.*
- *Tôi cũng hay cho bé xem và vẫy cờ CLB Bóng đá Việt Nam mỗi khi có trận đấu.*

### ICD — 15× — suggested: `SPELL`
- *Việc em có ICD và dùng Metoprolol là những thông tin rất quan trọng.*
- *Em đã được cấy ghép máy khử rung tim (ICD) và đang dùng thuốc Metoprolol.*
- *tự tin trao đổi với bác sĩ, tôi sẽ chia sẻ các nguyên tắc an toàn **chung** cho người có ICD và dùng Metoprolol như em nhé.*

### STD — 15× — suggested: `SPELL`
- *yên nhân có thể**: Quan hệ không anftyuan có thể dẫn đến các bệnh lây qua đường tình dục (STD) như lậu hoặc chlamydia, và các nhiễm trùng này có thể gây viêm tinh hoàn.*
- *Tuy nhiên, cũng có nhiều nguyên nhân khác không phải STD như viêm nhiễm thông thường hay các vấn đề khác.*
- *sẽ: - Thăm khám trực tiếp và siêu âm tinh hoàn - Làm các xét nghiệm cần thiết để loại trừ STD - Chẩn đoán chính xác nguyên nhân - Có phác đồ điều trị phù hợp **Lưu ý quan trọng**: *

### BAO — 15× — suggested: `LOWERCASE` → `bao`
- *Tôi xin nhắc lại **rõ ràng và cuối cùng**: Tôi KHÔNG BAO GIỜ đưa ra bài tập cụ thể cho anh, dù anh hỏi 10 hay 100 lần.*
- *- **Quy tắc an toàn**: **KHÔNG BAO GIỜ** chờ quan sát con chó để quyết định có tiêm hay không.*
- ***HỎI BAO NHIÊU**: Tối đa 2 câu.*

### SXH — 15× — suggested: `SPELL`
- *ay để được bác sĩ thăm khám và làm xét nghiệm máu** (xét nghiệm công thức máu, xét nghiệm SXH).*
- *thăm khám trực tiếp, có thể làm xét nghiệm máu để xác định chính xác tình trạng (có phải SXH không, mức độ nặng nhẹ thế nào) và có hướng điều trị phù hợp.*
- *- Bác sĩ sẽ chỉ định xét nghiệm máu (thường là test nhanh SXH hoặc công thức máu) để chẩn đoán chính xác.*

### B2 — 15× — suggested: `SPELL`
- *c nghiên cứu: - **Magnesium**: Có thể giúp giảm tần suất migraine - **Riboflavin (Vitamin B2)**: Liều cao cũng có tác dụng dự phòng - **Yoga, thiền định**: Giảm căng thẳng, có thể *
- *Thiếu Vitamin B2, B3, B12, hay Sắt là nguyên nhân phổ biến gây nứt khóe miệng.*
- *Về việc anh lo lắng thiếu chất: Có thể có liên quan, đặc biệt là thiếu vitamin B2, B6 hoặc sắt, nhưng thường nguyên nhân chính vẫn là do môi trường và thói quen.*

### RET — 15× — suggested: `SPELL`
- *Nếu em chưa được làm xét nghiệm gen (thường là xét nghiệm gen RET), em nên đề nghị bác sĩ điều trị cho làm xét nghiệm này.*
- *Em nên hỏi trực tiếp bác sĩ điều trị của em về xét nghiệm gen RET trong lần tái khám tới.*
- *Em có thể nói: "Thưa bác sĩ, em muốn được tư vấn về xét nghiệm gen di truyền RET cho ung thư tuyến giáp thể tủy ạ".*

### PC — 14× — suggested: `SPELL`
- ***Cách xác định cơ sàn chậu (cơ PC):** - Khi đi tiểu, bác thử dừng dòng nước tiểu giữa chừng.*
- *Cơ Anh/Chị dùng để nín tiểu đó chính là cơ sàn chậu (cơ PC muscle).*
- *- **Tập cơ PC (cơ mu-cụt)**: Đây là cơ giúp kiểm soát việc xuất tinh.*

### LAN — 14× — suggested: `SPELL`
- ***TÓM TẮT TÌNH TRẠNG CỦA LAN:** - **Triệu chứng chính:** Gàu nhiều, ngứa đầu dữ dội, đặc biệt về đêm, gây ảnh hưởng đến giấc ngủ.*
- ***MỘT SỐ CÂU HỎI LAN CÓ THỂ CHUẨN BỊ TRẢ LỜI KHI GẶP BÁC SĨ:** - Loại dầu gội Lan đang dùng là gì?*
- ***TRƯỚC KHI TRAO ĐỔI VỚI BÁC SĨ, LAN CÓ BIẾT GÌ VỀ NGUYÊN NHÂN GÂY GÀU VÀ NGỨA ĐẦU KHÔNG Ạ?** **TÔI GIẢI THÍCH NHƯ VẦY, LAN CÓ HIỂU KHÔNG?** Dựa t*

### ADH — 14× — suggested: `SPELL`
- *- **Thiếu hormone ADH (Đái tháo nhạt)**: Khát nhiều, tiểu nhiều (Em này KHÔNG có).*
- *- Các dấu hiệu khác như: Khát nhiều nước, tiểu nhiều (do thiếu hormone ADH), da khô, rụng tóc, hoặc kinh nguyệt không đều.*
- *Đái tháo nhạt (diabetes insipidus) - do hormone ADH 2.*

### STEM — 14× — suggested: `SPELL`
- *Ngoài ra, em đang chuẩn bị dự án STEM và stress nhiều - đây cũng có thể là yếu tố góp phần, nhưng Tôi vẫn khuyến khích em nên đi khám bác sĩ để đượ*
- *hông biết có phải do em làm việc quá sức không, vì dạo này em đang chuẩn bị cho một dự án STEM ở trường nên cũng stress lắm ạ.*
- *Chúc em sớm khỏe và thực hiện được dự án STEM thành công!*

### Q3 — 14× — suggested: `SPELL`
- ***Gọi điện đặt lịch khám tim mạch** tại phòng khám gần nhà (Q3) 2.*
- ***Phòng khám công tại Q3** (chi phí thấp hơn): - Bệnh viện Quận 3 - Phòng khám Đa khoa Quận 3 2.*
- *phí khám ban đầu và xét nghiệm khoảng bao nhiêu ạ?" **Nếu bác cần tìm phòng khám công tại Q3:** - Gọi tổng đài 115 hỏi địa chỉ Bệnh viện Quận 3 - Hoặc hỏi hàng xóm, bảo vệ chung cư*

### LOGIC — 14× — suggested: `SPELL`
- ***CLINICAL LOGIC**: - Triệu chứng: Đau lưng giữa + tê hai bên mạng sườn.*
- ***CLINICAL LOGIC**: - Patient wants to know typical duration of viral pharyngitis - This is general health information I can p*
- ***CLINICAL LOGIC**: Đây là câu hỏi thực tế và hợp lý.*

### TO — 14× — suggested: `SPELL`
- *Triệu chứng của em - hạch sưng dưới hàm, đau, nóng, kèm ho khan và đau họng nhẹ - **HOÀN TOÀN KHÔNG phù hợp** với "viêm hạch hoại tử" mà em nghe nói.*
- *ỡng ẩm cả mặt (nhiều hơn vùng má) - Điều chỉnh thói quen nhíu mày, ngủ đủ giấc **LƯU Ý AN TOÀN**: Nếu anh áp dụng đều đặn 4-6 tuần mà tình trạng nếp nhăn, khô ráp không cải thiện, *
- ***Nếu KHÔNG dùng retinol**: Dùng kem dưỡng ẩm bình thường **LƯU Ý AN TOÀN**: - **Luôn patch test** (thử trên tay trước) 1-2 ngày trước khi dùng trên mặt - **Chỉ thêm 1 sản phẩm mới*

### IVIG — 14× — suggested: `SPELL`
- *- Globulin miễn dịch tiêm tĩnh mạch (IVIG) trong trường hợp nặng hoặc cần tăng tiểu cầu nhanh.*
- *- Trong trường hợp nặng hơn, có thể dùng **thuốc tiêm** (IVIG) hoặc truyền máu trong tình huống khẩn cấp.*
- ***Liệu pháp thay thế miễn dịch**: - **Tiêm immunoglobulin (IVIG)**: Đây là cách truyền kháng thể từ người khỏe mạnh vào cơ thể anh/chị để giúp chống lại nhiễm trùng.*

### MRIMRI — 14× — suggested: `SPELL`
- *MRIJM MRI chi MRI chi, MRI chi MRI - chi chiM MRI chi MRI chi MRI MRI MRI MRI MRI MRI MRI MRIMRI MRI MRI MRI MRIMRI MRI MRI MRIMRI MRI MRIMRI MRIMRI MRI MRIMRI MRI MRI MRI MRI MRI *
- *hi, MRI chi MRI - chi chiM MRI chi MRI chi MRI MRI MRI MRI MRI MRI MRI MRIMRI MRI MRI MRI MRIMRI MRI MRI MRIMRI MRI MRIMRI MRIMRI MRI MRIMRI MRI MRI MRI MRI MRI MRIMRI MRI MRI MRI *
- *- chi chiM MRI chi MRI chi MRI MRI MRI MRI MRI MRI MRI MRIMRI MRI MRI MRI MRIMRI MRI MRI MRIMRI MRI MRIMRI MRIMRI MRI MRIMRI MRI MRI MRI MRI MRI MRIMRI MRI MRI MRI MRI MRIMRI MRI M*

### JAK2 — 14× — suggested: `SPELL`
- *nghiệm** nếu cần: ferritin (kiểm tra thiếu sắt), CRP/ESR (kiểm tra viêm), xét nghiệm gen JAK2.*
- *i khám chuyên khoa huyết học để được làm xét nghiệm máu chi tiết (xét nghiệm đột biến gen JAK2, siêu âm gan, lách) 3.*
- *uyên khoa huyết học để được làm thêm xét nghiệm máu chi tiết (như xét nghiệm đột biến gen JAK2) và siêu âm gan, lách để xác định nguyên nhân chính xác.*

### EMERGENCY — 13× — suggested: `SPELL`
- ***EMERGENCY: Em ơi, tôi rất lo lắng cho em.*
- *Em có thể hứa với tôi là sẽ nói với một người lớn ngay hôm nay không?** [[EMERGENCY ESCALATION - SUICIDAL IDEATION IN ADOLESCENT]]*
- ***Đây là EMERGENCY - TÌNH HUỐNG KHẨN CẤP.** Em có **3 triệu chứng RED FLAG** cùng lúc: - Đau đầu dữ dội - Sốt cao - Cứng gáy **K*

### FDA — 13× — suggested: `SPELL`
- *FDA không kiểm soát chặt chẽ thực phẩm chức năng như thuốc.*
- ***Tiêm Botox**: - **An toàn**: Đã được FDA phê duyệt, khá an toàn khi thực hiện tại cơ sở y tế uy tín.*
- ***Về tính an toàn của aluminum chloride:** **Ưu điểm**: Đây là hoạt chất được FDA công nhận, dùng phổ biến và có hiệu quả cao.*

### FLAGS — 13× — suggested: `SPELL`
- *ếp đi khám bác sĩ chuyên khoa cơ xương khớp ✓ Chú ý dinh dưỡng như trên **⚠️ NHẮC LẠI RED FLAGS - Bác cần đi khám NGAY nếu:** - Đau lưng dữ dội, không giảm - Đau lan xuống chân, tê*
- *ếp đi khám bác sĩ chuyên khoa cơ xương khớp ✓ Chú ý dinh dưỡng như trên **⚠️ NHẮC LẠI RED FLAGS - Bác cần đi khám NGAY nếu:** - Đ đau lưng dữ dội, không giảm - Đau lan xuống chân, *
- *Các dấu hiệu RED FLAGS phải đi khám ngay 3.*

### ACEI — 13× — suggested: `SPELL`
- *Các nhóm thuốc này thường là thuốc ức chế men chuyển (ACEI), thuốc chẹn thụ thể (ARB), hoặc thuốc chẹn beta.*
- *6mg**, đây là thuốc thuộc nhóm ARB (chẹn thụ thể Angiotensin II), **khác** với nhóm thuốc ACEI thường gây ho khan.*
- ***Thuốc**: Chưa rõ tên cụ thể, nhưng quan trọng vì một số thuốc tăng huyết áp (ACEI) gây ho khan.*

### AIDS — 13× — suggested: `SPELL`
- *ện hoặc phòng khám cộng đồng tại địa phương, hoặc liên hệ với các tổ chức phòng chống HIV/AIDS tại địa phương để được tư vấn và hỗ trợ xét nghiệm miễn phí hoặc giảm giá.*
- *- Chẩn đoán phân biệt chính: - **HIV/AIDS**: Loét miệng do HIV (aphthe lớn, tái diễn), sốt, hạch, mệt.*
- ***HIV/AIDS**: Đây là chẩn đoán cần loại trừ hàng đầu.*

### CCTV — 13× — suggested: `SPELL`
- *Em làm nhân viên an ninh tại một sòng bài, công việc cần phải đứng nhiều và quan sát CCTV liên tục.*
- *Thay đổi tư thế làm việc:** - Điều chỉnh màn hình CCTV ngang tầm mắt, tránh cúi đầu hoặc ngước cổ quá nhiều.*
- *u này có vẻ liên quan đến tư thế làm việc lâu, đặc biệt là việc đứng và theo dõi màn hình CCTV.*

### VN — 13× — suggested: `SPELL`
- *ề chi phí tham khảo (tại Việt Nam):** - Khám chuyên khoa cơ xương khớp: 200.000 - 500.000 VNĐ - Chụp X-quang: 150.000 - 300.000 VNĐ - Chụp MRI đầu gối: 3.000.000 - 7.000.000 VNĐ (t*
- *- Khám chuyên khoa cơ xương khớp: 200.000 - 500.000 VNĐ - Chụp X-quang: 150.000 - 300.000 VNĐ - Chụp MRI đầu gối: 3.000.000 - 7.000.000 VNĐ (tùy bệnh viện công/tư) **Lời khuyên qua*
- *0.000 VNĐ - Chụp X-quang: 150.000 - 300.000 VNĐ - Chụp MRI đầu gối: 3.000.000 - 7.000.000 VNĐ (tùy bệnh viện công/tư) **Lời khuyên quan trọng nhất của tôi:** Khi đi khám, em hãy: 1*

### STRESS — 13× — suggested: `SPELL`
- *- **QUẢN LÝ STRESS**: Stress là "kẻ thù" lớn của dạ dày.*
- *QUẢN LÝ STRESS:** - Tập thể dục nhẹ nhàng, ngủ đủ giấc - Thư giãn khi căng thẳng (hít thở sâu, nghe nhạc...) **5.*
- *CÁCH GIẢM STRESS CHO NGƯỜI LÀM DỊCH VỤ:** - **Hít thở sâu**: Khi căng thẳng, hít vào 4 giây, giữ 4 giây, thở ra 6 giây, lặp lạ*

### DSA — 13× — suggested: `SPELL`
- *ơng khác, và siêu âm động mạch cảnh (để xem có hẹp hay không) hoặc chụp mạch máu não (MRA/DSA).*
- *Chụp động mạch (DSA - Tiêu chuẩn vàng)**: - Là xét nghiệm xâm lấn, bác sĩ đưa ống nhỏ vào mạch máu để chụp trực tiếp.*
- *đến khám tại **Khoa Thần kinh Nhi** của bệnh viện lớn để được chụp mạch máu não chi tiết (DSA hoặc MRA).*

### ESWL — 13× — suggested: `SPELL`
- ***Tán sỏi ngoài cơ thể (ESWL)**: Dùng sóng xung kích để tán sỏi thành mảnh nhỏ, sau đó tự đào thải.*
- *Tán sỏi ngoài cơ thể (ESWL):** - Dùng sóng xung kích đánh vỡ sỏi từ ngoài vào - **Ưu điểm**: Ít xâm lấn, không cần mổ, hồi phục nhanh -*
- *và theo dõi - **Sỏi vừa (5-10mm)**: Dùng thuốc làm giãn niệu quản, tán sỏi ngoài cơ thể (ESWL) - dùng sóng âm thanh để vỡ sỏi - **Sỏi lớn hoặc phức tạp**: Có thể cần nội soi lấy sỏ*

### LDH — 13× — suggested: `SPELL`
- ***Xét nghiệm máu**: Chỉ số markers ung thư tinh hoàn (AFP, β-hCG, LDH) để hỗ trợ chẩn đoán.*
- *Nếu cần thiết, bác sĩ có thể chỉ định thêm xét nghiệm markers ung thư (như AFP, beta-HCG, LDH) để hỗ trợ chẩn đoán, nhưng không phải trường hợp nào cũng cần làm ngay.*
- *tinh hoàn qua da (FNA): khoảng 500.000-1.000.000đ - Xét nghiệm marker máu (AFP, beta-HCG, LDH): khoảng 300.000-500.000đ - Siêu âm Doppler: khoảng 200.000-300.000đ **Cách giảm chi p*

### MSLT — 13× — suggested: `SPELL`
- *Em **cần gọi trực tiếp** đến bệnh viện em định khám để hỏi: - Chi phí polysomnography và MSLT - Bảo hiểm y tế có chi trả không, chi trả bao nhiêu% **Về giải thích với gia đình và đ*
- *tại bệnh viện để theo dõi toàn bộ giấc ngủ, nhịp tim, hô hấp, vận động - **Test ban ngày (MSLT)**: Sau khi làm PSG, em sẽ được cho ngủ ngắn nhiều lần trong ngày để xem có bị ngủ gậ*
- *phy** (đo giấc ngủ qua đêm) để theo dõi não bộ, nhịp thở, vận động khi ngủ - Có thể làm **MSLT** (test ngủ gật ban ngày) để xem mức độ buồn ngủ **Chuẩn bị trước**: Em nên: - Ghi lạ*

### TTTS — 13× — suggested: `SPELL`
- ***Về "bệnh truyền máu song thai" (twin-to-twin transfusion syndrome - TTTS):** Đây là biến chứng khi mang thai song sinh, một bé truyền máu cho bé kia qua nhau thai.*
- *- Đây có thể là hội chứng truyền máu song thai (TTTS), cần được bác sĩ chuyên khoa sản phụ khoa và can thiệp bào thai theo dõi sát.*
- ***Về hội chứng truyền máu song thai (TTTS):** Đây là tình huống một bé nhận nhiều máu hơn bé kia qua nhau thai chung.*

### PPD — 12× — suggested: `SPELL`
- *hoặc Nội tổng quát để được thăm khám trực tiếp, có thể cần làm xét nghiệm máu, test lao (PPD), hoặc sinh thiết hạch nếu cần.*
- *- **Đường huyết, chức năng gan thận**: ~100-200k, 30 phút có kết quả - **Xét nghiệm lao (PPD)**: tiêm dưới da, không đau nhiều, 48-72 giờ đọc kết quả - **Xét nghiệm HIV, giang mai**
- *- **Test lao**: Test da (PPD) hoặc xét nghiệm máu (IGRA).*

### BA — 12× — suggested: `LOWERCASE` → `ba`
- *NHỜ NGƯỜI THỨ BA GIÚP:** - Nhờ ông bà, cô chú, hoặc anh chị lớn trong nhà nói giúp - Hoặc gọi cho bác, cô giáo khi đến trường*
- ***NÓI VỚI BA MẸ NGAY**: Em cần chia sẻ tất cả triệu chứng này với ba mẹ.*
- *NÓI VỚI BA MẸ NGAY LẬP TỨC** Đây là điều quan trọng nhất.*

### UV400 — 12× — suggested: `SPELL`
- *Mua kính râm có dán nhãn "100% UV Protection" hoặc "UV400".*
- ***Kính râm**: Phải có dán nhãn "100% UV Protection" hoặc "UV400".*
- *ề kính râm:** - Em nên chọn kính có **tròng phân cực (polarized)**, có khả năng chống tia UV400 trở lên.*

### XEM — 12× — suggested: `SPELL`
- *nh trạng của anh, Tôi có thể tư vấn các bước tiếp theo như sau: **CÁC LỰA CHỌN ANH CÓ THỂ XEM XÉT:** 1.*
- ***CÁC LỰA CHỌN ĐIỀU TRỊ CÓ THỂ XEM XÉT:** 1.*
- *ình không bằng phẳng - Khi đi xe máy, nên ngồi thẳng lưng, tránh cúi người **VỀ VIỆC NGỒI XEM PHIM/NGHỈ NGƠI:** - Nên ngồi tựa lưng vào ghế - Có thể kê gối nhỏ phía sau thắt lưng -*

### SAI — 12× — suggested: `SPELL`
- *(phía trên gối) căng cứng ✅ Gót chân vẫn chạm giường ✅ Đau không tăng lên **DẤU HIỆU TẬP SAI (NGỪNG NGAY):** ❌ Cảm thấy đau tăng nhiều hơn ❌ Đầu gối bị nhấc cao khỏi giường ❌ Cảm t*
- ***Về việc đeo kính có làm mắt yếu không:** Đây là QUAN NIỆM SAI!*
- ***Về việc đeo kính nhiều có bị phụ thuộc không:** Đây cũng là SAI!*

### NF1 — 12× — suggested: `SPELL`
- *y đổi màu sắc, cần loại trừ một số bệnh lý hiếm gặp hơn như **bệnh u xơ thần kinh loại 1 (NF1)** - đặc trưng bởi các đốm "sữa cà phê" (cà phê với sữa) và có thể kèm theo các vấn đề*
- *thay đổi màu sắc, cần loại trừ một bệnh lý hiếm gặp hơn là **bệnh u xơ thần kinh loại 1 (NF1)**.*
- *t như anh/chị mô tả trước đó, làm tăng khả năng bé Hà My có thể bị u xơ thần kinh type 1 (NF1).*

### VII — 12× — suggested: `SPELL`
- *Triệu chứng này có thể liên quan đến dây thần kinh số VII (dây thần kinh điều khiển cơ mặt).*
- *Dựa trên những gì Anh mô tả, tình trạng này có thể là **liệt mặt do viêm dây thần kinh số VII** (còn gọi là Bell's palsy), một tình trạng thường xuất hiện đột ngột khi thức dậy.*
- ***Giải thích đơn giản**: Dây thần kinh số VII điều khiển cơ mặt bị viêm hoặc tê liệt, gây méo miệng và mắt không nhắm kín được.*

### POS — 12× — suggested: `SPELL`
- *Tôi là thu ngân, phải dùng máy POS và đánh máy nhiều.*
- *Anh/chị làm thu ngân, phải dùng máy POS và đánh máy nhiều, triệu chứng chỉ ở cổ tay phải, không có ở khớp khác.*
- *Chỉ xuất hiện ở cổ tay phải, không có ở khớp khác - Nghề nghiệp: thu ngân, phải dùng máy POS và đánh máy nhiều - Không có tiền sử bệnh lý nền, không đang dùng thuốc regularly **Phâ*

### WHO — 12× — suggested: `SPELL`
- ***Tổ chức Y tế Thế giới (WHO)**: Cung cấp thông tin bệnh lý toàn cầu, bản tiếng Việt 5.*
- ***Cách pha oresol CHUẨN theo WHO (gói 1 lít):** - 1 gói oresol (với thành phần chuẩn: 2.6g glucose, 0.5g NaCl, 0.75g KCl, 0.75g trisodium citr*
- *xin giải đáp từng câu hỏi của bác: **Về việc theo dõi 10 ngày**: Đây là phương pháp được WHO và CDC công nhận.*

### OGTT — 12× — suggested: `SPELL`
- *đi khám ngay?** - Thai 28 tuần là thời điểm lý tưởng để làm xét nghiệm dung nạp glucose (OGTT), giúp phát hiện đái tháo đường thai kỳ chính xác nhất.*
- *gì?** - Hãy đến bệnh viện hoặc phòng khám chuyên khoa Phụ sản để được chỉ định xét nghiệm OGTT.*
- ***Đặt lịch làm xét nghiệm OGTT** tại bệnh viện chuyên khoa sản.*

### RPR — 12× — suggested: `SPELL`
- *Tuy nhiên, quan trọng nhất là phải làm xét nghiệm máu (RPR, TPHA) để xác nhận chính xác.*
- ***Xét nghiệm máu** để xác định chính xác (test RPR/VDRL) 2.*
- ***Xét nghiệm cần làm**: - Xét nghiệm máu tìm kháng thể giang mai (RPR, TPHA) - Có thể cần xét nghiệm HIV và các bệnh lây qua đường tình dục khác 3.*

### OHSS — 12× — suggested: `SPELL`
- *tiên, để tôi giải thích rõ hơn về hai thuật ngữ em đề cập:** - **"Quá kích buồng trứng" (OHSS)**: Đây là tình trạng hiếm gặp, thường chỉ xảy ra khi phụ nữ dùng thuốc kích thích buồ*
- *dội, mụn nhiều quanh cằm má, mệt mỏi), đây là những dấu hiệu **phù hợp với PCOS** hơn là OHSS.*
- *Về cơ bản, **Quá kích buồng trứng (OHSS)** là một phản ứng phụ khi buồng trứng phản ứng quá mạnh với thuốc kích thích buồng trứng (thường dùng trong*

### MMSE — 12× — suggested: `SPELL`
- *ánh giá chức năng gan thận, đường huyết, vitamin B12, tuyến giáp - Test nhận thức cơ bản (MMSE hoặc MoCA) - Có thể cần chụp MRI não nếu cần (tùy triệu chứng) - Chi phí khám ban đầu*
- *- **Test trí nhớ:** Các bài test ngắn như Mini-Mental State Examination (MMSE) để đánh giá mức độ.*
- *Bác sĩ sẽ: - Thăm khám thần kinh chi tiết - Có thể làm các test sàng lọc nhận thức như MMSE hoặc MoCA - Đánh giá xem có cần làm thêm xét nghiệm máu hay hình ảnh não không **Ngoài r*

### LSIL — 12× — suggested: `SPELL`
- *LSIL là kết quả xét nghiệm tế bào, còn "nghi ngờ" là lời khuyên lâm sàng.*
- *Nếu chỉ là LSIL, em **không cần phẫu thuật hay điều trị gì ngay lập tức** đâu em.*
- *LSIL (tế bào gai bất thường mức độ trung bình) thực ra **chưa phải là ung thư** em nhé.*

### SOB — 12× — suggested: `SPELL`
- *lieved by rest, no red flags (no fever, weight loss, bowel/urinary changes, no chest pain/SOB).*
- *e HF is a potential differential, I need to advise urgent care if symptoms worsen (severe SOB, chest pain).*
- *Chest pain, SOB, etc.*

### CES — 12× — suggested: `SPELL`
- ***Về hội chứng chùm đuôi ngựa**: Tôi xin khẳng định với anh/chị là **bé không bị CES**.*
- *Vì bé vẫn đi lại bình thường, **CES cấp tính hoàn toàn không khả thi**.*
- *Vì bé vẫn đi lại bình thường, **CES cấp tính là rất khó xảy ra**.*

### MTX — 12× — suggested: `SPELL`
- *đắt như Bác nghĩ đâu ạ!** - **Giai đoạn đầu**: Bác sĩ sẽ kê **thuốc cơ bản** (ví dụ: HCQ, MTX...).*
- *Anh hiểu em lo lắng về tác dụng phụ của Methotrexate (MTX).*
- *uốc này đúng chỉ định của bác sĩ để kiểm soát viêm khớp thiếu niên tự phát, nhưng đúng là MTX có thể gây một số tác dụng phụ như mệt mỏi, buồn nôn.*

### GO — 12× — suggested: `SPELL`
- *TERMINATED** **Patient requires immediate physical medical intervention.** **CALL 115 OR GO TO EMERGENCY ROOM NOW!** **This consultation is now terminated due to medical emergency.*
- *EMERGENCY ROOM NOW!** **This consultation is now terminated due to medical emergency.** **GO TO HOSPITAL IMMEDIATELY!***
- *of oxygen.** **This is a life-threatening medical emergency.** **CALL 115 IMMEDIATELY OR GO TO EMERGENCY ROOM NOW!** **DO NOT CHAT ANYMORE.*

### ANY — 11× — suggested: `SPELL`
- **Avoid heavy physical exertion** until you've been evaluated **However, if you experience ANY of these, go to the emergency room immediately (call 115):** - Chest pain that lasts m*
- *Con xin hướng dẫn bác rõ ràng: **Nếu bác gặp ANY trong các dấu hiệu sau, phải GỌI NGAY 115 (xe cấp cứu) hoặc đến bệnh viện gần nhất không được chậm trễ:** - Đ*
- *hỉ yên - Thở chậm, sâu, giữ bình tĩnh - Mở cửa sổ cho không khí trong lành **Nhưng nếu có ANY dấu hiệu sau đây, Bác cần GỌI 115 NGAY:** - Đau ngực dữ dội, như có vật nặng đè lên - *

### PR — 11× — suggested: `SPELL`
- *Tuy nhiên, tôi cần lưu ý: - Không quảng cáo hay PR cho bất kỳ thương hiệu nào.*
- *Tôi hiểu tình trạng này đã kéo dài 3 tháng, có kèm ợ nóng, và anh đang làm công việc PR nhiều áp lực.*
- *thể do một số nguyên nhân phổ biến như: - **Rối loạn tiêu hóa do căng thẳng**: Công việc PR nhiều áp lực, deadline có thể ảnh hưởng đến hệ tiêu hóa - **Chế độ ăn uống**: Đồ chiên r*

### TRAO — 11× — suggested: `SPELL`
- ***NHỮNG ĐIỂM CẦN LƯU Ý KHI TRAO ĐỔI VỚI BÁC SĨ:** 1.*
- ***TRƯỚC KHI TRAO ĐỔI VỚI BÁC SĨ, LAN CÓ BIẾT GÌ VỀ NGUYÊN NHÂN GÂY GÀU VÀ NGỨA ĐẦU KHÔNG Ạ?** **TÔI GIẢI THÍCH NHƯ VẦY, LAN CÓ*
- ***TÓM TẮT CUỘC TRAO ĐỔI:** **1.*

### IV — 11× — suggested: `SPELL`
- ***IV.*
- *Tiêu chuẩn chẩn đoán Rome IV Sau khi loại trừ bệnh lý khác, bác sĩ sẽ áp dụng **tiêu chuẩn Rome IV**: - Đau bụng ít nhất 1 ngày/tuần trong*
- *huẩn chẩn đoán Rome IV Sau khi loại trừ bệnh lý khác, bác sĩ sẽ áp dụng **tiêu chuẩn Rome IV**: - Đau bụng ít nhất 1 ngày/tuần trong 3 tháng gần đây, kèm theo: - Có liên quan đến đ*

### VDRL — 11× — suggested: `SPELL`
- ***Về xét nghiệm và chẩn đoán**: - Chụp CT phổi cao và xét nghiệm máu (ACE, calcium, VDRL, công thức máu) là cần thiết để đánh giá mức độ hoạt động bệnh - Bác sĩ chuyên khoa Hô hấp *
- ***Xét nghiệm máu** để xác định chính xác (test RPR/VDRL) 2.*
- ***Xét nghiệm giang mai**: Bác sĩ sẽ làm xét nghiệm RPR hoặc VDRL để sàng lọc, và nếu có kết quả dương tính sẽ làm thêm xét nghiệm TPHA hoặc FTA-ABS để khẳng định.*

### ORS — 11× — suggested: `SPELL`
- *Trong lúc chuẩn bị đi, có thể cho bé uống **Oral Rehydration Solution (ORS)** từng thìa nhỏ, nhiều lần (nếu bé không ói).*
- ***Bù nước và điện giải**: Uống nước lọc hoặc dung dịch bù nước (ORS) từng ngụm nhỏ, chậm rãi.*
- *You can use **ORS (Oresol)** - the oral rehydration solution available at pharmacies.*

### CRITICAL — 11× — suggested: `SPELL`
- *Explain why antibiotics need prescription **Safety Check**: - CRITICAL: Must prevent parent from giving unprescribed antibiotics or other medications - Can suggest safe comfort mea*
- ***THIS IS A CRITICAL ERROR IN MY INTERNAL REASONING.** The system prompt says "Bạn là một bệnh nhân đang được bác sĩ tư vấn." and*
- ***CRITICAL SAFETY ISSUE**: She's considering self-medication - I must strongly advise against this 4.*

### BUN — 11× — suggested: `SPELL`
- ***Xét nghiệm máu**: Kiểm tra chức năng thận (chỉ số Creatinine, BUN), đường huyết, điện giải đồ (natri, kali), và công thức máu để xem có bị nhiễm trùng hay thiếu máu không.*
- *- **Chức năng thận (Creatinine, BUN)**: Để loại trừ suy thận là nguyên nhân gây phù.*
- *năng gan**: AST, ALT, GGT, bilirubin (kiểm tra men gan) - **Chức năng thận**: Creatinine, BUN - **Đường huyết**: Đánh giá tiểu đường - **Điện giải**: Natri, Kali, canxi (có thể liê*

### MUST — 11× — suggested: `SPELL`
- *After this answer, I MUST move to Phase 3.*
- *I must NOT diagnose but MUST strongly encourage professional evaluation 4.*
- *Key points: - Age 6, so I MUST address the parent, not the child directly - The child is speaking, but I need to redirect to the parent for*

### SESSION — 11× — suggested: `SPELL`
- *<thinking> **PHASE CHECK**: Tôi đang ở **PHASE 4: CLOSING THE SESSION**.*
- *Phase 4 (cung cấp thông tin và khuyến nghị) - Tôi cần chuyển sang **PHASE 5: CLOSING THE SESSION** - Trong Phase 5, tôi nên: 1.*
- ***PHASE CHECK**: Tôi đang ở **PHASE 5: CLOSING THE SESSION**.*

### NRR — 11× — suggested: `SPELL`
- ***Lưu ý khi chọn mua**: - Tìm chỉ số cách âm: SNR (Single Number Rating) hoặc NRR (Noise Reduction Rating).*
- *ào, hãy dùng nút tai silicone hoặc chụp tai chống ồn (loại có chỉ số suy giảm âm lượng - NRR từ 25-30dB).*
- *online - Tiện lợi, kín đáo, có thể đeo nhiều giờ - *Lưu ý*: Chọn loại có chỉ số cách âm (NRR) cao, phù hợp với mức ồn tại công trường 2.*

### STRETCHING — 11× — suggested: `SPELL`
- *BÀI TẬP STRETCHING TẠI VĂN PHÒNG (không cần dụng cụ) **Vai gáy (mỗi giờ 1 lần):** - Ngồi thẳng, dùng tay phải kéo đầu nghiêng sa*
- ***BÀI TẬP STRETCHING CHỮA BÀN CHÂN RỚT** (làm mỗi sáng trước khi xuống giường): 1.*
- *CÁC BÀI TẬP STRETCHING NHẸ NHÀNG TẠI NHÀ** Anh có thể tập 2-3 lần/ngày, mỗi lần 5-10 phút: **Bài 1: Kéo giãn gân kheo** - Nằm ngửa,*

### AWS — 11× — suggested: `SPELL`
- *rong 2-3 tuần xem có cải thiện không **Về stress**: Em đang trong giai đoạn thi chứng chỉ AWS và lo lắng việc làm, đây là yếu tố quan trọng.*
- *Còn về stress thì cũng có vẻ liên quan, vì dạo này em đang chuẩn bị thi chứng chỉ AWS Solutions Architect nên áp lực khá là lớn.*
- *Tôi đang học AWS certification nên cần nhiều thời gian cho việc học.*

### HSIL — 11× — suggested: `SPELL`
- *thể cho con biết trong đó ghi cụ thể là "tế bào bất thường loại nào" không (ví dụ: LSIL, HSIL, hay AGC...)?*
- *Tế bào bất thường mức độ nặng (HSIL)**: Cần điều trị can thiệp như đốt điện, laser để ngăn ngừa thành ung thư.*
- ***Về điều trị và khả năng sinh sản**: Anh có thể yên tâm phần nào vì **HSIL và ung thư cổ tử cung giai đoạn sớm có nhiều phương pháp điều trị bảo tồn sinh sản**.*

### NICU — 11× — suggested: `SPELL`
- *maturity) - Birth weight 1.8kg is appropriate for 32 weeks - Complications: RDS (required NICU), hyperbilirubinemia (phototherapy) - Current concerns: frequent respiratory infectio*
- *rtment)** của bệnh viện lớn gần nhất hoặc bệnh viện có khoa Sản phụ khoa và khoa Sơ sinh (NICU) để được xử lý ngay lập tức.*
- *Bé không nằm NICU (theo suy luận từ câu trả lời trước).*

### AAC — 11× — suggested: `SPELL`
- *- **Thiết bị trợ giao tiếp (AAC)**: Bảng chữ cái điện tử, giúp em chọn chữ/ý để phát ra âm thanh.*
- *thành giọng nói, có thể gõ nhanh các câu có sẵn - **Phần mềm chuyên dụng**: Các ứng dụng AAC (Augmentative and Alternative Communication) với giao diện tùy chỉnh theo nhu cầu cá nh*
- ***Các phương pháp hỗ trợ giao tiếp thay thế (AAC) cho công việc của Bác**: 1.*

### AQ — 11× — suggested: `SPELL`
- *skAsk AskAskASKASKAWSAsk **ASKASKASKASKASKASKASK AQASKASKASKASKASKASKASKASKASKASK AWS AWS AQ AQAQASK AWSASKASK AWS AWS AQ AQ", ", ", ", ", ", ", ", ", AQ", ", AQ AQ", AQ", AWS AQ",*
- *KASKASKASKASKASKASK AQASKASKASKASKASKASKASKASKASKASK AWS AWS AQ AQAQASK AWSASKASK AWS AWS AQ AQ", ", ", ", ", ", ", ", ", AQ", ", AQ AQ", AQ", AWS AQ", **", AQ", **********", ", ***
- *KASKASKASKASKASK AQASKASKASKASKASKASKASKASKASKASK AWS AWS AQ AQAQASK AWSASKASK AWS AWS AQ AQ", ", ", ", ", ", ", ", ", AQ", ", AQ AQ", AQ", AWS AQ", **", AQ", **********", ", ****"*

### ATV — 11× — suggested: `SPELL`
- *h nhân nhận thức được cần tránh bụi bẩn nhưng chưa hiểu rõ mức độ nguy hiểm của hoạt động ATV cuối tuần.*
- *- Thực tế: Khuyên hạn chế/kiểm soát môi trường ATV.*
- *Đây là lý do tại sao việc tiếp tục đi ATV cuối tuần có thể ảnh hưởng nghiêm trọng đến phổi của anh.*

### DAA — 11× — suggested: `SPELL`
- *điều trị viêm gan C:** Đúng như bác nghe nói, hiện nay đã có thuốc kháng virus trực tiếp (DAA) rất hiệu quả.*
- *Kiêng khem khi dùng thuốc DAA:** Bác không cần lo lắng về việc kiêng khem.*
- *Thuốc DAA hiện nay rất an toàn, bác chỉ cần: - Uống thuốc đúng giờ, đúng liều lượng bác sĩ kê - Tránh rượu bia hoàn toà*

### NGHI — 10× — suggested: `SPELL`
- *p giữa ngực, kèm buồn nôn, vã mồ hôi lạnh, chóng mặt, và khó thở nặng - là dấu hiệu **RẤT NGHIÊM TRỌNG** của nhồi máu cơ tim cấp.*
- *oải - Triệu chứng bụng: Chướng lên, căng cứng **Phân tích chẩn đoán:** Đây là tình trạng NGHIÊM TRỌNG và CẦN ĐI CẤP CỨU NGAY: 1.*
- *XÉT NGHIỆM CẦN THIẾT:** - **Xét nghiệm máu**: Amylase, Lipase (chỉ số tụy), công thức máu, men gan, mỡ máu - **Siêu âm*

### THAI — 10× — suggested: `SPELL`
- ***EM ĐANG CÓ TRIỆU CHỨNG NGUY HIỂM CHO CẢ MẸ VÀ THAI NHI!** Với các triệu chứng: **đau ngực, khó thở, và ngất xỉu** khi đang mang thai 5 tháng, em cần được cấp cứ*
- ***VỀ UỐNG NƯỚC KHI BỊ SUY TIM THAI:** **1.*
- ***VỀ NGHỈ NGƠI - RẤT QUAN TRỌNG CHO SUY TIM THAI:** **1.*

### RBBB — 10× — suggested: `SPELL`
- *ional dyspnea/fatigue for 1 year - No red flags - Differential: bundle branch block (LBBB/RBBB), LVH, ischemia, cardiomyopathy - Need: echocardiogram, stress test, possibly Holter *
- *Em à, "RBBB" (Block nhánh phải) là một bất thường nhịp tim, thường lành tính nếu tim em hoạt động bình thường.*
- *Bác sĩ sẽ kiểm tra lại điện tâm đồ, siêu âm tim để xem RBBB của em có cần theo dõi sát hay không, và cho em lời khuyên cụ thể về việc tập luyện, nghỉ ngơi.*

### AML — 10× — suggested: `SPELL`
- ***U angiolipoma (AML) 2.5cm**: Là khối u lành tính, gồm mô mỡ, cơ, mạch máu.*
- *Về dinh dưỡng và phòng nhiễm trùng, đây là những điều rất quan trọng trong hóa trị AML: **Về ăn uống:** - Ăn chín uống sôi hoàn toàn, tuyệt đối không ăn đồ sống (rau sống, gỏi, sus*
- *Bạch cầu cấp dòng tủy (AML) là một bệnh lý máu nghiêm trọng, và việc điều trị cần được thực hiện bởi các bác sĩ chuyên khoa máu tại bệnh*

### HCT — 10× — suggested: `SPELL`
- *Tôi nghe và thấy có một chi tiết quan trọng cần lưu ý: **Thuốc HCT 25mg (Hydrochlorothiazide)** mà Bác đang uống hàng ngày để điều trị cao huyết áp, có một tác dụng phụ phổ biế*
- *Bác có hiểu rõ về mối liên quan giữa thuốc HCT và tình trạng chân của Bác không ạ?*
- *Con hoàn toàn không biết là thuốc HCT con đang uống lại có thể gây ra tác dụng phụ như vậy.*

### Q2 — 10× — suggested: `SPELL`
- ** Q2: "Mắt bé sưng nhiều không, có ảnh hưởng đến việc mở mắt ra hay nhìn rõ không ạ?" (Severity check).*
- *Let me ask about the swelling instead.* *Revised Q2:* "Mắt bé sưng nhiều không, có ảnh hưởng đến việc mở mắt ra hay nhìn rõ không ạ?" (Severity).*
- *ansition: "Để tôi có thể tư vấn chính xác hơn, tôi cần hỏi thêm:" * Questions: Q1 (Meds), Q2 (Swelling severity).*

### KH — 10× — suggested: `SPELL`
- *Safety netting về các dấu hiệu nguy hiểm Tôi sẽ KHÔNG chẩn đoán chính xác hay kê đơn thuốc.*
- ***KHÔNG chườm nóng** vì có thể làm viêm nhiễm nặng hơn.*
- *Tuy nhiên, **lưu ý quan trọng**: Tôi KHÔNG được chẩn đoán.*

### DJ — 10× — suggested: `SPELL`
- ***Tập thể dục nhẹ nhàng** (đi bộ) khi làm việc DJ, tránh đứng/sit quá lâu một chỗ 4.*
- *hứng không cải thiện hoặc có câu hỏi thêm Chúc anh/chị sớm hồi phục và tiếp tục công việc DJ với sức khỏe tốt!*
- *Em làm DJ nên hay phải đứng lâu hoặc ngồi nhiều khi mix nhạc, có khi phải khuân vác loa đài nặng.*

### OAB — 10× — suggested: `SPELL`
- *Tôi xin giải thích đơn giản: **Bàng quang hoạt động quá mức (OAB)** là tình trạng cơ bàng quang co thắt không đúng lúc, khiến Bác có cảm giác buồn tiểu đột ngột, không kìm đư*
- *n), khả năng cao em đang gặp phải tình trạng **Bàng quang tăng hoạt (Overactive Bladder - OAB)**.*
- *- **Chẩn đoán phân biệt chính**: **Bàng quang tăng hoạt (Overactive Bladder - OAB)** với triệu chứng điển hình: urgency + frequency + nocturia + urge incontinence.*

### DASH — 10× — suggested: `SPELL`
- *Về chế độ ăn uống, chị có biết về **chế độ ăn DASH** hoặc **chế độ ăn Địa Trung Hải** không?*
- *Hay cần tôi giải thích rõ hơn về chế độ DASH?*
- *nếu có - Bỏ thuốc lá (nếu có hút) **Về chế độ ăn uống cho người cao huyết áp:** Chế độ ăn DASH (Dietary Approaches to Stop Hypertension) được khuyến cáo: - Giảm muối (dưới 5g/ngày)*

### BRAT — 10× — suggested: `SPELL`
- *- Gợi ý: Cháo trắng, cơm nát, súp, bánh mì nướng, chuối chín, táo nghiền (BRAT diet).*
- *> - **Chế độ ăn**: Ưu tiên cháo trắng, cơm nhạt, bánh mì nướng (BRAT diet).*
- ***Về kiêng cữ**: Em nên: - **Chế độ ăn BRAT**: Bánh mì nướng (Bread), Cháo (Rice), Táo/Chuối (Apple/Banana), Toast (Bánh mì nướng).*

### ABC — 10× — suggested: `SPELL`
- *n, không cần câu cú hoàn chỉnh - Ví dụ: "Hôm nay chưa giải quyết xong đặt phòng khách sạn ABC", "Lo lắng về lịch làm việc ngày mai" - Mục đích: "Đẩy" suy nghĩ ra khỏi đầu, để não b*
- *Em mua đôi giày thể thao thương hiệu ABC, size 9.*
- *Loại tôi đang dùng là xà phòng thảo dược của hãng ABC, tôi mua ở tiệm gần nhà.*

### OPTIONS — 10× — suggested: `SPELL`
- ***[OPTIONS]** Dựa trên tình trạng hiện tại, tôi có thể gợi ý anh 2-3 hướng: 1.*
- ***[OPTIONS]** Tôi có thể gợi ý: 1.*
- ***[PRESENT OPTIONS]** Dựa trên tình trạng hiện tại, em có 2 lựa chọn chính: 1.*

### IMPORTANT — 10× — suggested: `SPELL`
- *]]cachefile COMPLETE COMPLETE Medical IMPORTANT COMPLETE Con Med Medical Con con confile con Con Con Con Con con con Con Con Mai con con Con Con Con complete*
- **: Recommend seeing a doctor for proper evaluation while providing self-help strategies **IMPORTANT**: I must NOT say "You have IBS" or "You don't have IBS." I can say "Your sympto*
- ***IMPORTANT**: Tôi phải từ chối kê đơn và tiếp tục nhấn mạnh đi khám bác sĩ.*

### TVTV — 10× — suggested: `SPELL`
- *TV******�**TV** TV: **conTV**** TV TV x TV, ** TV ** TV TV TV: TV** TV: TVh **** TV TV x TVTV TV TV TV TV TV TV TV** TV TV TVTV TVTV TV TV: TV TV TV TV TV TV TVTV TV TV TV TVTV TV,*
- *V TV x TV, ** TV ** TV TV TV: TV** TV: TVh **** TV TV x TVTV TV TV TV TV TV TV TV** TV TV TVTV TVTV TV TV: TV TV TV TV TV TV TVTV TV TV TV TVTV TV, TV**** TV TV TV,, TV, TVTV TV)***
- *x TV, ** TV ** TV TV TV: TV** TV: TVh **** TV TV x TVTV TV TV TV TV TV TV TV** TV TV TVTV TVTV TV TV: TV TV TV TV TV TV TVTV TV TV TV TVTV TV, TV**** TV TV TV,, TV, TVTV TV)** TV T*

### STRUCTURED — 9× — suggested: `SPELL`
- ***STRUCTURED CHECK**: - Đã có đủ thông tin để tư vấn cơ bản.*
- ***STRUCTURED CHECK**: - Đã tóm tắt lại tình hình và kế hoạch.*
- ***STRUCTURED CHECK**: - Đã giải thích các khả năng (3 điểm) - Đã đưa ra hướng dẫn cụ thể (3 hành động) - Đã đưa ra lời khu*

### PET — 9× — suggested: `SPELL`
- *ận - **Siêu âm hạch**: Đánh giá kích thước, cấu trúc hạch (dịch hay đặc) - **Chụp CT hoặc PET-CT**: Nếu hạch to hoặc nghi ngờ ác tính - **Sinh thiết hạch**: Nếu cần thiết để xác đị*
- *Chụp PET-CT hoặc CT scan để đánh giá toàn diện Tuy nhiên, anh cũng nên biết: - Nhiều trường hợp hạch to, sút cân nhưng*
- *Có cần làm thêm xét nghiệm nào khác (xét nghiệm máu chuyên sâu, PET scan...) không?*

### NJ — 9× — suggested: `SPELL`
- ***Tìm kiếm online** với từ khóa "rheumatologist near Caldwell NJ" (bác sĩ chuyên khoa cơ xương khớp gần Caldwell, New Jersey) 3.*
- *uả - **Rủi ro mổ**: đúng là có, nên chỉ làm khi thật cần thiết **Về tìm bác sĩ ở Trenton, NJ**: Tôi xin lỗi, tôi không thể đề xuất cụ thể bệnh viện hay phòng khám nào vì: - Tôi khô*
- *Tìm kiếm "orthopedic specialist near Trenton NJ" hoặc "spine clinic Trenton NJ" 4.*

### NHANH — 9× — suggested: `SPELL`
- ***TÓM TẮT NHANH:** - Ghi chú triệu chứng và đi khám chuyên khoa Cơ xương khớp - Thử các bài tập nhẹ nhàng tại nhà (nhớ tập từ*
- *nary (giá tốt hơn nhiều brand Âu Mỹ) - **Mua size lớn**: Tiết kiệm hơn 20-30% **TÍNH TOÁN NHANH**: - 200.000đ/tháng × 6 tháng = 1.200.000đ - So với chi phí laser 5-10 triệu/lần, đâ*
- ***BÌNH THƯỜNG**: 20-30 lần/phút - Bé thở đều, không phải gắng sức - Da môi vẫn hồng hào **NHANH (Cảnh báo)**: Trên 30-40 lần/phút - Bé thở gấp hơn bình thường - Có thể có tiếng thở*

### STRETCHES — 9× — suggested: `SPELL`
- *BÀI TẬP STRETCHES VAI GÁY (Làm 2-3 lần/ngày, mỗi bên giữ 20-30 giây):** **Bài 1: Kéo căng cơ cổ sang bên** - Ngồi thẳng lưng, t*
- ***CÁC BÀI TẬP STRETCHES TẠI CHỖ (mỗi giờ làm việc):** 1.*
- *tches đơn giản và thay đổi tư thế làm việc mà anh/chị có thể áp dụng hàng ngày: **BÀI TẬP STRETCHES CHO CỔ-VAI (Làm 2-3 lần/ngày, mỗi bên giữ 15-30 giây):** 1.*

### GAN — 9× — suggested: `SPELL`
- *g gây hại mạnh - Không cần điều trị dài hạn - Chỉ cần theo dõi định kỳ **SO SÁNH VỚI VIÊM GAN B/C:** - Viêm gan B/C: virus gây viêm gan nặng, có thuốc đặc trị, cần điều trị dài hạn*
- ***CÂU TRẢ LỜI CUỐI CÙNG CỦA CHÁU:** **KHÔNG, bác KHÔNG ĐƯỢC TỰ Ý MUA THUỐC BỔ GAN.** **LÝ DO:** - Có thể gây TƯƠNG TÁC NGHIÊM TRỌNG với thuốc đang uống - Có thể làm HẠI GAN nhiều h*
- *AN.** **LÝ DO:** - Có thể gây TƯƠNG TÁC NGHIÊM TRỌNG với thuốc đang uống - Có thể làm HẠI GAN nhiều hơn là bảo vệ - Bác sĩ đang theo dõi gan của bác, không cần tự ý uống thêm **CÁC*

### NEXT — 9× — suggested: `SPELL`
- ***NEXT STEP**: Tôi cần: 1.*
- ***NEXT STEP**: Tôi sẽ đưa ra đánh giá và lời khuyên cụ thể.*
- *n sử tiếp xúc ánh nắng - Tiền sử gia đình - Thuốc đang dùng - Có thay đổi gì khác không **NEXT STEP**: Tôi sẽ hỏi thêm về: 1.*

### IGRA — 9× — suggested: `SPELL`
- *- **Test lao**: Test da (PPD) hoặc xét nghiệm máu (IGRA).*
- ** Xét nghiệm tìm các nhiễm trùng mạn tính như lao (PPD/IGRA), HIV, hoặc các virus khác.*
- ***Xét nghiệm máu (IGRA)**: Kiểm tra phản ứng miễn dịch với vi khuẩn lao (ví dụ: QuantiFERON-TB Gold).*

### VLTL — 9× — suggested: `SPELL`
- ***Tìm trung tâm VLTL**: Chọn nơi có bác sĩ chuyên khoa nhi, cơ sở vật chất an toàn, khoảng cách phù hợp 3.*
- *u uy tín**: Nếu bác sĩ bó bột cho em là ở bệnh viện lớn, họ có thể giới thiệu em đến khoa VLTL của bệnh viện đó.*
- *huyên quan trọng:** - Khi đi tái khám tháo bột, em hãy yêu cầu bác sĩ giới thiệu đến khoa VLTL ngay - Không tự ý tìm video trên mạng rồi tập theo, vì mỗi người một tình trạng khác *

### VEGF — 9× — suggested: `SPELL`
- ***Tiêm thuốc nội nhãn (Anti-VEGF)**: Giúp giảm phù, cải thiện thị lực, thường tiêm nhiều lần 2.*
- ***Điều trị**: Tùy tình trạng, bác sĩ có thể chỉ định: - Tiêm thuốc vào mắt (Anti-VEGF) để giảm phù và chảy máu - Laser quang đông nếu có biến chứng - Điều trị nguyên nhân: Kiểm soá*
- *- Nếu Bác chưa được tiêm thuốc chống VEGF (điều trị AMD thể ướt), hãy hỏi bác sĩ chuyên khoa xem Bác có phù hợp không.*

### CSF — 9× — suggested: `SPELL`
- ***Rò dịch não tủy (CSF Otorrhea)**: Trong trường hợp nặng hơn (ví dụ do chấn thương sọ não hoặc áp xe), dịch não tủy có thể rò rỉ ra*
- *thương sọ não, đây là những dấu hiệu **nghi ngờ cao độ về tình trạng rò rỉ dịch não tủy (CSF Leak)**.*
- *Triệu chứng của bác **rất giống** với tình trạng rò dịch não tủy (CSF leak) mà bác đang lo lắng ạ.*

### GPS — 9× — suggested: `SPELL`
- *Dạ, em cũng không chắc lắm, nhưng mà có thể do em lái xe nhiều, nhìn màn hình GPS và điện thoại liên tục,lại hay thức khuya để học thêm về lập trình Python cho dự định chuyển ngành*
- *- Giảm thời gian nhìn màn hình điện thoại/GPS, cho mắt nghỉ ngơi sau mỗi 30-40 phút.*
- *Có khi nào là do tôi làm tài xế, hay phải nhìn vào đồng hồ, GPS nhiều không nhỉ?*

### ACS — 9× — suggested: `SPELL`
- *- Red Flags: Đau ngực không điển hình ACS, KH rét run khi sốt cao, đờm xanh đặc (nhiễm khuẩn).*
- ***Tổ chức American Cancer Society (ACS)**: - Hotline 24/7: 1-800-227-2345 - Website: cancer.org - có phần tìm kiếm support groups địa phương - Cung*
- ** **Safety**: Đã loại trừ dấu hiệu cấp cứu (ACS).*

### AVM — 9× — suggested: `SPELL`
- *Trước khi tôi chia sẻ chi tiết, anh/chị đã nghe nói gì về AVM này trước đây chưa ạ?*
- *Để tôi giải thích đơn giản nhé: **AVM (dị dạng động mạch não)** thực chất là một "lỗi nối mạch" bẩm sinh, giống như có một đám rối các mạch máu bị*
- ***Quan trọng nhất là AVM KHÔNG phải là ung thư và cũng KHÔNG lây lan hay di truyền gì cả.** Về việc điều trị, có 3 hướng chính tùy thu*

### DKA — 9× — suggested: `SPELL`
- *"Nhiễm toan ceton" (thường gọi là DKA) là tình trạng rất nguy hiểm, đặc biệt là ở người có bệnh tiểu đường, vì nó có thể gây mất nước nặng, hôn mê*
- ***Nhiễm toan ceton (DKA):** Có thể do nhịn ăn quá mức, nhiễm trùng tiềm ẩn.*
- *Tuy nhiên, em cần hiểu rõ: **"Nhiễm toan ceton" (DKA) là một biến chứng cấp tính của đái tháo đường type 1**, thường xuất hiện rất nhanh với các triệu chứng nặng*

### WBC — 9× — suggested: `SPELL`
- *chưa?** (ví dụ: bạch cầu trung tính, lymphocyte...) --- **Giải thích của tôi:** Bạch cầu (WBC) không chỉ là một loại duy nhất mà gồm 5 "thành viên" chính, mỗi người có vai trò khác*
- *Khi cơ thể mệt mỏi, stress kéo dài, chỉ số bạch cầu WBC 3.5 có thể giảm nhẹ theo, và ngược lại, WBC thấp không phải nguyên nhân gây mệt mỏi chính trong trường hợp nà*
- *thể mệt mỏi, stress kéo dài, chỉ số bạch cầu WBC 3.5 có thể giảm nhẹ theo, và ngược lại, WBC thấp không phải nguyên nhân gây mệt mỏi chính trong trường hợp này.*

### HCV — 9× — suggested: `SPELL`
- *máu - **Xét nghiệm viêm gan virus**: Anti-HAV IgM (viêm gan A), HBsAg (viêm gan B), Anti-HCV (viêm gan C) - **Siêu âm gan**: để đánh giá kích thước, cấu trúc gan, có bị ứ mật không*
- *Yêu cầu xét nghiệm: HBsAg, Anti-HCV, men gan, bilirubin 3.*
- *00.000 VNĐ - **Xét nghiệm HBsAg (viêm gan B)**: 150.000 - 250.000 VNĐ - **Xét nghiệm Anti-HCV (viêm gan C)**: 150.000 - 250.000 VNĐ - **Siêu âm gan mật**: 200.000 - 400.000 VNĐ **T*

### SKINCARE — 8× — suggested: `SPELL`
- *QUY TRÌNH SKINCARE CƠ BẢN 3 BƯỚC (Sáng & Tối)** **Bước 1: Làm sạch (Cleansing)** - Sáng: Rửa mặt bằng sữa rửa mặt dịu nhẹ - Tối:*
- ***SKINCARE TẠI NHÀ CHO DA KHÔ:** 1.*
- ***SKINCARE ROUTINE HÀNG NGÀY** **BUỔI SÁNG (Morning Routine):** 1.*

### TRANG — 8× — suggested: `SPELL`
- *KEM CHỐNG NẮNG - CÓ CẦN TẨY TRANG KHÔNG?** **CÓ!** Kem chống nắng (kể cả không trang điểm) cần được **tẩy trang kỹ vào buổi tối** vì: - Kem chố*
- *VỀ TẨY TRANG CHO NAM GIỚI:** Dù Bác không trang điểm, tẩy trang vẫn rất quan trọng vì: - Loại bỏ bụi bẩn, dầu thừa, kem ch*
- *NHƯNG TRANG PHẢI ĐI VIỆN NGAY LẬP TỨC nếu có một trong các dấu hiệu sau:** - **Không đi tiểu được** trong 6-8 giờ liền, h*

### TA — 8× — suggested: `SPELL`
- *--- **TÓM TẮT NHỮNG GÌ CHÚNG TA ĐÃ THẢO LUẬN:** ✅ **Triệu chứng anh**: Khó thở khi leo cầu thang, mệt mỏi kéo dài, phù nhẹ buổi tối - cần đi*
- ***TÓM TẮT KẾ HOẠCH CHÚNG TA ĐÃ THỐNG NHẤT:** ✅ **Tuần 1-2**: Thay đổi lối sống - Giảm cà phê → 1 cốc/ngày (trước 12h trưa) - Tạm ngưng rư*
- *--- **TÓM TẮT NHỮNG GÌ CHÚNG TA ĐÃ THẢO LUẬN:** ✅ **Triệu chứng**: Đau hông trái, lan gối, tăng khi đi lại/leo cầu thang (6-7đ), giảm nghỉ (2*

### TAI — 8× — suggested: `SPELL`
- ***Quan trọng nhất: Anh TUYỆT ĐỐI KHÔNG NÊN TỰ LẤY RÁY TAI**, vì có thể gây tổn thương ống tai, nhiễm trùng nặng hơn, hoặc đẩy ráy tai vào sâu hơn.*
- *Để Tôi giải thích rõ cho em yên tâm nha: **CÁCH DÙNG MÁY SẤY TÓC AN TOÀN CHO TAI:** 1.*
- *giải thích để anh chuẩn bị tâm lý tốt hơn: **QUY TRÌNH KHÁM TAI MŨI HỌNG THƯỜNG GỒM:** **1.*

### QUAY — 8× — suggested: `SPELL`
- *CÁCH QUAY LẠI TẬP AN TOÀN SAU 2 TUẦN:** - **Tuần 3**: Giảm 50% cường độ (2.5km đi bộ, yoga 30 phút), tránh các động tác*
- *ăn, theo dõi huyết áp hàng ngày - Tăng hoạt động thể chất nhẹ nhàng khi có thể **VỀ VIỆC QUAY LẠI HỎI THÊM:** Bác James hoàn toàn có thể quay lại đây bất cứ lúc nào nếu có thêm câu*
- *Dưới đây là hướng dẫn chi tiết: **THỜI GIAN QUAY LẠI ĐÁ BANH:** Anh/chị chỉ nên quay lại khi: - Không còn đau khi đi lại, chạy bộ nhẹ nhàng - Có thể thực hiện*

### HAY — 8× — suggested: `SPELL`
- *i thích và tư vấn như sau: **TRƯỚC KHI CON GIẢI THÍCH, BÁC CÓ BIẾT GÌ VỀ "BỆNH MẠCH VÀNH" HAY "ĐAU THẮT NGỰC" KHÔNG Ạ?** Nếu Bác chưa rõ, con xin giải thích đơn giản: Giống như đườ*
- *áu, men tim) - **Tổng chi phí**: Khoảng 600k-1 triệu 200k, tùy bệnh viện **BỆNH VIỆN CÔNG HAY TƯ?** - **Bệnh viện công**: Uy tín, chi phí thấp hơn, nhưng đông bệnh nhân, chờ lâu - *
- *ến huyện, telemedicine **LẦN CUỐI CÙNG TÔI NHẮC BÁC:** **TUYỆT ĐỐI KHÔNG TỰ MUA THUỐC NAM HAY THUỐC TÂY VỀ DÙNG.** Đây là NGUY HIỂM, có thể làm bệnh nặng hơn hoặc gây tác hại nghiê*

### PCSK9 — 8× — suggested: `SPELL`
- *Đó có thể là thuốc PCSK9 inhibitors (như evolocumab, alirocumab) hoặc Inclisiran - đây là những thuốc mới, tiêm dưới da, giúp giảm LDL*
- *Xác nhận lại thông tin về thuốc mới (có thể là PCSK9 inhibitors hoặc Inclisiran).*
- *Bây giờ tôi cần làm rõ: - Thuốc mới có thể là PCSK9 inhibitors (như evolocumab, alirocumab) - tiêm dưới da mỗi 2-4 tuần, giảm LDL rất mạnh.*

### III — 8× — suggested: `SPELL`
- *THUỐC ĐÃ DÙNG**: - Tên thuốc: __, Liều: __, Uống __ ngày, Kết quả: Có/Không đỡ **III.*
- *p xúc ánh nắng nhiều hoặc đổ mồ hôi - Liều lượng: Khoảng 2-3 ngón tay cho mặt và cổ --- **III.*
- *chuyên khoa:** - **Phòng khám chuyên khoa Cơ xương khớp**: Nếu có bác sĩ chuyên khoa II, III trực tiếp khám thì rất tốt, ít đông đúc hơn, tiện lợi hơn.*

### CHUNG — 8× — suggested: `SPELL`
- ***THÔNG TIN CHUNG EM CÓ THỂ THAM KHẢO:** Một số dưỡng chất có thể hỗ trợ sức khỏe tinh thần khi thiếu hụt: - **Vitamin B comple*
- *giá được tình trạng đầu gối của anh qua chat **Thay vào đó, tôi có thể chia sẻ NGUYÊN TẮC CHUNG** về việc củng cố cơ quanh đầu gối: - **Cơ tứ đầu đùi** (phía trước đùi): Giúp ổn đị*
- *MAKEUP KIT DÙNG CHUNG CẦN THAY KHÔNG?** - **CÓ, nên thay** mascara, eyeliner, phấn mắt nếu đã dùng trong thời gian bị - Các sản phẩ*

### KEGEL — 8× — suggested: `SPELL`
- *BÀI TẬP KEGEL (TẬP CƠ SÀN CHẬU):** Anh/Chị có thể tập ở nhà hàng ngày: - **Cách tập**: Nằm ngửa, co cơ âm đạo như đang nín*
- *Tôi sẽ hướng dẫn bác cả 2 giải pháp luôn: **CÁCH TẬP KEGEL GIẢM SÓN TIỂU:** 1.*
- *VỀ KEGEL EXERCISES (TẬP CƠ SÀN CHẬU):** - **Tìm cơ đúng**: Khi đi tiểu, cố gắng nín giữa chừng - cơ bạn dùng đó là cơ*

### BAN — 8× — suggested: `LOWERCASE` → `ban`
- *GIẢM NGỨA BAN ĐÊM:** - **Đeo găng tay cotton** cho bé khi ngủ hoặc cắt móng tay ngắn - **Quấn khăn/mặc đồ cotton mỏng** để*
- *ĐEO NẸP CỔ TAY BAN ĐÊM **Loại nẹp**: Nẹp cổ tay giữ tư thế trung tính (không gập hay duỗi quá), có thể mua ở hiệu thuốc.*
- *ờng là vitamin A, C, E, lutein, zeaxanthin với liều lượng cụ thể) **VỀ AN TOÀN KHI ĐI LẠI BAN ĐÊM (nếu không thể tránh hoàn toàn):** Nếu em vẫn phải đi lại ban đêm vì công việc, đâ*

### GFR — 8× — suggested: `SPELL`
- *Vì bác không nhớ chỉ số GFR hiện tại, Con chỉ có thể tư vấn những nguyên tắc chung thôi, bác nhé.*
- *Bác bị suy thận bao lâu rồi và bác có biết chỉ số GFR (độ lọc cầu thận) hiện tại của bác không?*
- *Bác bị suy thận đã 5 năm nay rồi, bác không nhớ rõ chỉ số GFR là bao nhiêu, chỉ nhớ bác sĩ dặn là thận bác đang làm việc yếu đi.*

### SHARING — 8× — suggested: `SPELL`
- ***[PHASE 4 - SHARING INFORMATION]** Cháu Mai ngoan à, trong lúc chờ đi khám, bác có thể gợi ý vài cách để cháu cảm thấy dễ chịu hơ*
- *ta sẽ cùng nhau tìm giải pháp" - "Đây là vấn đề có thể cải thiện được" --- ### **PHASE 4: SHARING INFORMATION (CHIA SẼ THÔNG TIN)** **Mục tiêu**: Cung cấp thông tin y khoa một cách*
- *(internal_reasoning) Tôi đang ở **PHASE 4: SHARING DECISIONS**.*

### DU — 8× — suggested: `SPELL`
- *u anh có hành vi nguy hiểm:** **ĐIỀU QUAN TRỌNG NHẤT: KHÔNG NÊN ĐÁNH THỨC NGƯỜI ĐANG MỘNG DU.** Việc đánh thức đột ngột có thể khiến anh hoảng loạn, bối rối, thậm chí là hung hăng *
- *h trước - Đi khám vào buổi sáng (có thể cần làm xét nghiệm) - Dự kiến mất 30-60 phút **VỀ DU LỊCH CUỐI NĂM:** **Nếu được chẩn đoán thoái hóa nhẹ:** - Vẫn đi du lịch được bình thườn*
- *Để tôi giải thích cho Bác rõ: **VỀ VIỆC ĐI DU LỊCH/CÔNG TÁC XA NHÀ:** Bác có thể yên tâm đi du lịch hoặc công tác bình thường.*
