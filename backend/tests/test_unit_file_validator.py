"""文件校验模块单元测试。

覆盖范围：
- 扩展名校验
- MIME类型校验
- 文件大小校验
- 文件名安全校验
- 路径遍历检测
- 内容类型深度校验
"""

from __future__ import annotations

import pytest

from app.core.file_validator import FileValidator, ValidationResult, validate_upload_file


class TestFileValidatorBasic:
    """基础文件校验测试。"""

    def test_valid_pdf(self):
        """测试合法PDF文件应通过校验。"""
        # PDF文件头: %PDF-1.4
        file_bytes = b"%PDF-1.4\n1 0 obj\n<<\n/Type /Catalog\n>>\nendobj\n"
        result = FileValidator.validate(file_bytes, "resume.pdf", "application/pdf")
        assert result.is_valid is True
        assert result.detected_mime == "application/pdf"

    def test_valid_txt(self):
        """测试合法TXT文件应通过校验。"""
        file_bytes = b"Hello, this is my resume content."
        result = FileValidator.validate(file_bytes, "resume.txt", "text/plain")
        assert result.is_valid is True
        assert result.detected_mime == "text/plain"

    def test_valid_png(self):
        """测试合法PNG文件应通过校验（FileValidator支持图片）。"""
        # PNG文件头
        png_bytes = b'\x89PNG\r\n\x1a\n' + b'\x00' * 100
        result = FileValidator.validate(png_bytes, "avatar.png", "image/png")
        assert result.is_valid is True
        assert "image/png" in result.detected_mime

    def test_invalid_content_type_detection(self):
        """测试内容类型不匹配应被识别。"""
        # 声称是PDF但实际是纯文本且非txt扩展名
        file_bytes = b"This is plain text content"
        result = FileValidator.validate(file_bytes, "resume.pdf", "application/pdf")
        assert result.is_valid is False
        assert "无法识别" in result.error

    def test_file_too_large(self):
        """测试超大文件应被拒绝。"""
        file_bytes = b"x" * (10 * 1024 * 1024 + 1)
        result = FileValidator.validate(file_bytes, "resume.pdf", "application/pdf")
        assert result.is_valid is False
        assert "大小" in result.error


class TestUploadFileValidation:
    """上传文件前置校验测试（validate_upload_file函数）。"""

    def test_valid_upload(self):
        """测试合法上传应通过。"""
        validate_upload_file("resume.pdf", "application/pdf", 1024)

    def test_invalid_extension_upload(self):
        """测试不合法扩展名上传应被拒绝。"""
        with pytest.raises(ValueError, match="不支持的文件扩展名"):
            validate_upload_file("file.exe", "application/octet-stream", 1024)

    def test_invalid_mime_upload(self):
        """测试不合法MIME上传应被拒绝。"""
        with pytest.raises(ValueError, match="不支持的 MIME 类型"):
            validate_upload_file("file.pdf", "image/png", 1024)

    def test_oversized_upload(self):
        """测试超大文件上传应被拒绝。"""
        with pytest.raises(ValueError, match="文件大小超过限制"):
            validate_upload_file("file.pdf", "application/pdf", 20 * 1024 * 1024)

    def test_path_traversal_filename(self):
        """测试路径遍历文件名应被拒绝（通过扩展名校验时）。"""
        with pytest.raises(ValueError, match="非法路径遍历字符"):
            validate_upload_file("..\\..\\etc\\passwd.txt", "text/plain", 1024)

    def test_empty_filename(self):
        """测试空文件名应被拒绝。"""
        with pytest.raises(ValueError, match="文件名缺少扩展名"):
            validate_upload_file("", "application/pdf", 1024)

    def test_filename_too_long(self):
        """测试超长文件名应被拒绝。"""
        long_name = "a" * 260 + ".pdf"
        with pytest.raises(ValueError, match="文件名长度超过限制"):
            validate_upload_file(long_name, "application/pdf", 1024)


class TestSecurityEdgeCases:
    """安全边界情况测试。"""

    def test_null_bytes_in_filename(self):
        """测试文件名中包含null字节的处理。"""
        # null字节可能导致扩展名提取异常，这里验证函数不会崩溃
        try:
            validate_upload_file("file\x00.pdf", "application/pdf", 1024)
            # 如果没有抛出异常，至少函数应该正常返回
        except ValueError:
            # 抛出ValueError是可接受的
            pass

    def test_double_extension_attack(self):
        """测试双重扩展名攻击应被正确处理。"""
        with pytest.raises(ValueError, match="不支持的文件扩展名"):
            validate_upload_file("file.pdf.exe", "application/octet-stream", 1024)

    def test_unicode_filename(self):
        """测试Unicode文件名应被接受。"""
        validate_upload_file("简历.pdf", "application/pdf", 1024)

    def test_case_insensitive_extension(self):
        """测试扩展名应大小写不敏感。"""
        validate_upload_file("resume.PDF", "application/pdf", 1024)
        validate_upload_file("resume.DOCX", "application/vnd.openxmlformats-officedocument.wordprocessingml.document", 1024)

    def test_validation_result_dataclass(self):
        """测试ValidationResult数据类的基本功能。"""
        result = ValidationResult(is_valid=True, detected_mime="application/pdf", error="")
        assert result.is_valid is True
        assert result.detected_mime == "application/pdf"
        assert result.error == ""

        result2 = ValidationResult(is_valid=False, error="invalid")
        assert result2.is_valid is False
        assert result2.error == "invalid"
        assert result2.detected_mime == ""
