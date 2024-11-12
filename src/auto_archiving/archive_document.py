from json_config import IssueType, ConfigJson
from src.shared.log import Log


class ArchiveDocument():
    def __init__(self, path: str):
        print(Log.getting_something_from
              .format(another=path,
                      something=Log.archive_document_content))
        with open(path, 'r', encoding="utf-8") as file:
            self.__lines = file.readlines()
            self.__new_lines: list[str] = []
            self.__reverse_lines = self.__lines[::-1]
            self.__lines_set = set(self.__lines)
        print(Log.getting_something_from_success
              .format(another=path,
                      something=Log.archive_document_content))
        self.__file = open(path, 'w', encoding="utf-8")

    def __add_line(self, line: str) -> None:
        self.__new_lines.append(line)

    def __get_table_last_line_index(self) -> int:
        line_index = 0
        for index, line in enumerate(self.__reverse_lines, 1):
            if line.strip():
                line_index = index
                break
        return len(self.__lines) - line_index

    def __get_last_table_number(
        self,
        table_separator: str
    ) -> int:
        # 后面的写入到归档文件函数会把归档序号+1，所以这里得0
        result = 0
        table_last_line = self.__lines[
            self.__get_table_last_line_index()
        ]
        start = table_last_line.find(table_separator)
        end = table_last_line.find(table_separator, start+1)
        if (temp := table_last_line[start+1:end]).isdigit():
            print(Log.got_archive_number
                  .format(
                      archive_number=temp
                  ))
            result = int(temp)
        else:
            print(Log.unexpected_archive_number
                  .format(
                      default_number=result +1,
                      line=table_last_line 
                  ))
        
        return result

    @staticmethod
    def parse_issue_title(
        issue_title: str,
        issue_type: str,
        issue_title_processing_rules: dict[IssueType,
                                           ConfigJson.ProcessingAction]
    ) -> str:
        action_map = issue_title_processing_rules.get(
            issue_type)
        if action_map is None:
            return issue_title
        else:
            result = issue_title
            for keyword in action_map["remove_keyword"]:
                result.replace(keyword, '')
            result = ''.join(
                [action_map["add_prefix"],
                 result,
                 action_map["add_suffix"]]
            )
            return result

    def should_issue_archived(self, issue_id: int) -> bool:
        sub_string = f'Issue#{issue_id}]'
        for line in self.__lines_set:
            if sub_string in line:
                print(
                    Log.issue_id_found_in_archive_record
                    .format(issue_id=issue_id)
                )
                return True
        print(
            Log.issue_id_not_found_in_archive_record
            .format(issue_id=issue_id)
        )
        return False

    def archive_issue(self,
                      rjust_space_width: int,
                      rjust_character: str,
                      table_separator: str,
                      archive_template: str,
                      issue_title_processing_rules: dict[IssueType,
                                                         ConfigJson.ProcessingAction],
                      issue_id: int,
                      issue_type: str,
                      issue_title: str,
                      issue_repository: str,
                      introduced_version: str,
                      archive_version: str
                      ) -> None:
        print(Log.format_issue_content)
        new_line = archive_template.format(
            table_id=self.__get_last_table_number(
                table_separator) + 1,

            issue_type=issue_type,
            issue_title=ArchiveDocument.parse_issue_title(
                issue_title,
                issue_type,
                issue_title_processing_rules
            ),
            rjust_space=((rjust_space_width
                          - len(issue_title))
                         * rjust_character),
            issue_repository=issue_repository,
            issue_id=issue_id,
            introduced_version=introduced_version,
            archive_version=archive_version
        )
        if "\n" not in new_line:
            new_line += "\n"
        self.__add_line(new_line)
        print(Log.format_issue_content_success)

    def save(self) -> None:
        print(Log.write_content_to_document)
        self.__lines.insert(
            self.__get_table_last_line_index() + 1,
            *self.__new_lines
        )
        self.__file.writelines(
            self.__lines
        )
        print(Log.write_content_to_document_success)

    def close(self) -> None:
        self.__file.close()
