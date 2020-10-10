FROM satel/python-base:3.2.1

# Install pip packages
RUN pip install mkautodoc markdown-include --user

CMD ["./StartDocs.sh"]
